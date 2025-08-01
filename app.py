# app.py
import streamlit as st
import requests, io, zipfile
import re

st.title("Bulk SmartMap Downloader – QLD")

st.markdown("""
Paste Lot/Plan entries (one per line). Supported formats include:

- `3/SP181800`  
- `3SP181800`  
- `Lot 3 on Survey Plan 181800`  
- `Lot 2 on RP24834`  
- `5RP12345`
""")

lot_input = st.text_area("Enter Lot/Plan combinations")
if st.button("Generate & Download ZIP"):
    entries = [line.strip() for line in lot_input.splitlines() if line.strip()]
    if not entries:
        st.error("Please enter at least one Lot/Plan")
    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
            for entry in entries:
                m = re.search(r"(\d+)\s*(?:on)?\s*(?:registered plan|rp|survey plan|sp)\s*(\d+)", entry, re.IGNORECASE)
                if m:
                    lot = m.group(1)
                    plan_num = m.group(2)
                    prefix = "RP" if re.search(r"(rp|registered)", entry, re.IGNORECASE) else "SP"
                else:
                    m2 = re.match(r"(\d+)\s*(RP|SP)\s*(\d+)", entry, re.IGNORECASE)
                    if m2:
                        lot = m2.group(1)
                        prefix = m2.group(2).upper()
                        plan_num = m2.group(3)
                    else:
                        st.write(f"⚠️ Could not parse: '{entry}'")
                        continue

                code = f"{lot}%5C{prefix}{plan_num}"
                url = f"https://apps.information.qld.gov.au/data/cadastre/GenerateSmartMap?q={code}"
                resp = requests.get(url)
                fname = f"{lot}_{prefix}{plan_num}.pdf"
                if resp.status_code == 200:
                    zipf.writestr(fname, resp.content)
                    st.write(f"✅ Downloaded: {fname}")
                else:
                    st.write(f"⚠️ Failed {entry}: HTTP {resp.status_code}")

        zip_buf.seek(0)
        st.download_button(
            "📥 Download ZIP of SmartMaps",
            data=zip_buf,
            file_name="SmartMaps_Qld.zip",
            mime="application/zip",
        )
