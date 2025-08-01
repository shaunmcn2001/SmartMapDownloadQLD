# app.py
import streamlit as st
import requests
import io
import zipfile

st.title("Bulk SmartMap Downloader - QLD")

lot_input = st.text_area("Enter Lot/Plan combinations (e.g. `12/RP24834` ), one per line")
if st.button("Generate & Download"):
    entries = [line.strip() for line in lot_input.splitlines() if line.strip()]
    if not entries:
        st.error("Please enter at least one Lot/Plan")
    else:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for entry in entries:
                try:
                    lot, plan = entry.replace("\\","/").split("/")
                    plan = plan.strip()
                    lot = lot.strip()
                    prefix = "RP" if plan.upper().startswith("RP") else ("SP" if plan.upper().startswith("SP") else plan)
                    code = f"{lot}%5C{prefix}{plan.replace(prefix,'')}"
                    url = f"https://apps.information.qld.gov.au/data/cadastre/GenerateSmartMap?q={code}"
                    resp = requests.get(url)
                    if resp.status_code == 200:
                        fname = f"{lot}_{prefix}{plan}.pdf"
                        zipf.writestr(fname, resp.content)
                        st.write(f"✅ Downloaded {fname}")
                    else:
                        st.write(f"⚠️ Failed {entry}: HTTP {resp.status_code}")
                except Exception as e:
                    st.write(f"⚠️ Error parsing '{entry}': {e}")
        zip_buffer.seek(0)
        st.download_button(
            "📥 Download All as ZIP",
            data=zip_buffer,
            file_name="SmartMaps_Qld.zip",
            mime="application/zip"
        )
