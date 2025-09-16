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
- `1/BN100`
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
                type_match = re.search(
                    r"(\d+)\s*(?:on)?\s*(registered plan|rp|survey plan|sp|crown plan|cp|plan)\s*([A-Za-z]{1,4})?\s*(\d+)",
                    entry,
                    re.IGNORECASE,
                )
                if type_match:
                    lot = type_match.group(1)
                    plan_type = type_match.group(2).lower()
                    explicit_prefix = type_match.group(3)
                    plan_num = type_match.group(4)
                    if explicit_prefix:
                        prefix = explicit_prefix.upper()
                    else:
                        prefix = {
                            "registered plan": "RP",
                            "rp": "RP",
                            "survey plan": "SP",
                            "sp": "SP",
                            "crown plan": "CP",
                            "cp": "CP",
                        }.get(plan_type)
                        if prefix is None:
                            st.write(f"⚠️ Could not determine plan prefix for: '{entry}'")
                            continue
                else:
                    entry_clean = entry.strip()
                    m2 = re.match(
                        r"(\d+)\s*[/\\-]?\s*([A-Za-z]{1,4})\s*(\d+)",
                        entry_clean,
                        re.IGNORECASE,
                    )
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
