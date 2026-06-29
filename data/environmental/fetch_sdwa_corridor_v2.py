"""
Downloads EPA ECHO's SDWA (Safe Drinking Water Act) national dataset and
filters to public water systems in the Allegheny Trail corridor counties.

REQUIREMENTS:
    pip install pandas requests

OUTPUT:
    sdwa_corridor_systems.csv       - all PWS in corridor counties, with
                                       population served and system type
    sdwa_corridor_small_systems.csv - subset serving <500 people (highest
                                       vulnerability to demand spikes)
    sdwa_corridor_violations.csv    - violation history for corridor systems

NOTE: This version prints the actual column names from
SDWA_PUB_WATER_SYSTEMS.csv before filtering, since ECHO's schema has changed
field names across versions (e.g. COUNTY_SERVED vs COUNTIES_SERVED).
"""

import zipfile
import io
import os
import requests
import pandas as pd

URL = "https://echo.epa.gov/files/echodownloads/SDWA_latest_downloads.zip"
LOCAL_ZIP = "SDWA_latest_downloads.zip"

CORRIDOR_COUNTIES = [
    "PRESTON", "TUCKER", "RANDOLPH", "POCAHONTAS", "GREENBRIER", "MONROE",
]

# --- Download (cache locally so re-runs don't re-download) ---
if not os.path.exists(LOCAL_ZIP):
    print("Downloading SDWA dataset (this is a large file, may take a while)...")
    resp = requests.get(URL, stream=True)
    resp.raise_for_status()
    with open(LOCAL_ZIP, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {os.path.getsize(LOCAL_ZIP) / 1e6:.1f} MB")
else:
    print(f"Using cached {LOCAL_ZIP} ({os.path.getsize(LOCAL_ZIP) / 1e6:.1f} MB)")

zf = zipfile.ZipFile(LOCAL_ZIP)

# --- Step 1: inspect columns before filtering ---
with zf.open("SDWA_PUB_WATER_SYSTEMS.csv") as f:
    pws = pd.read_csv(f, dtype=str, low_memory=False, nrows=5)

print("\nColumns in SDWA_PUB_WATER_SYSTEMS.csv:")
for c in pws.columns:
    print("  -", c)

# --- Step 2: identify the state and county columns dynamically ---
state_col = next((c for c in pws.columns if c.upper() in
                   ("STATE_CODE", "PRIMACY_STATE", "STATE")), None)
county_col = next((c for c in pws.columns if "COUNT" in c.upper() and "SERV" in c.upper()), None)
pop_col = next((c for c in pws.columns if "POPULATION_SERVED" in c.upper()), None)

print(f"\nDetected columns -> state: {state_col}, county: {county_col}, population: {pop_col}")

if state_col is None or county_col is None:
    print("\nCould not auto-detect required columns. Please inspect the column "
          "list above and update the script with the correct names, e.g.:")
    print('  state_col = "STATE_CODE"')
    print('  county_col = "COUNTIES_SERVED"')
    raise SystemExit(1)

# --- Step 3: re-read full file now that we know the columns ---
with zf.open("SDWA_PUB_WATER_SYSTEMS.csv") as f:
    pws = pd.read_csv(f, dtype=str, low_memory=False)

pws_wv = pws[pws[state_col] == "WV"].copy()
print(f"\n{len(pws_wv)} total WV public water systems")

if pop_col:
    pws_wv[pop_col] = pd.to_numeric(pws_wv[pop_col], errors="coerce")

mask = pws_wv[county_col].str.upper().fillna("").apply(
    lambda x: any(c in x for c in CORRIDOR_COUNTIES)
)
corridor_pws = pws_wv[mask].copy()
print(f"{len(corridor_pws)} systems match corridor counties "
      f"({', '.join(CORRIDOR_COUNTIES)})")

# Save everything for this subset (don't over-filter columns until we've
# confirmed the schema)
corridor_pws.to_csv("sdwa_corridor_systems.csv", index=False)
print("Wrote sdwa_corridor_systems.csv (all columns)")

# --- Step 4: small systems ---
if pop_col:
    small = corridor_pws[corridor_pws[pop_col] < 500]
    small.sort_values(pop_col).to_csv("sdwa_corridor_small_systems.csv", index=False)
    print(f"{len(small)} systems serve fewer than 500 people "
          f"-> sdwa_corridor_small_systems.csv")

# --- Step 5: violations ---
pwsid_col = "PWSID" if "PWSID" in corridor_pws.columns else None
if pwsid_col:
    corridor_ids = set(corridor_pws[pwsid_col])
    with zf.open("SDWA_VIOLATIONS_ENFORCEMENT.csv") as f:
        viol = pd.read_csv(f, dtype=str, low_memory=False)
    viol_corridor = viol[viol[pwsid_col].isin(corridor_ids)]
    viol_corridor.to_csv("sdwa_corridor_violations.csv", index=False)
    print(f"{len(viol_corridor)} violation records -> sdwa_corridor_violations.csv")

print("\nDone.")
