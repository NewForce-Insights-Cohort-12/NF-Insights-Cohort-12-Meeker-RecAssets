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
"""

import zipfile
import io
import requests
import pandas as pd

URL = "https://echo.epa.gov/files/echodownloads/SDWA_latest_downloads.zip"

# Counties the Allegheny Trail corridor passes through (5-mile buffer)
CORRIDOR_COUNTIES = [
    "PRESTON", "TUCKER", "RANDOLPH", "POCAHONTAS", "GREENBRIER", "MONROE",
]

print("Downloading SDWA dataset (this is a large file, may take a while)...")
resp = requests.get(URL, stream=True)
resp.raise_for_status()

zf = zipfile.ZipFile(io.BytesIO(resp.content))
print("Files in archive:")
for n in zf.namelist():
    print("  -", n)

# --- Public water systems table ---
with zf.open("SDWA_PUB_WATER_SYSTEMS.csv") as f:
    pws = pd.read_csv(f, dtype=str, low_memory=False)

pws_wv = pws[pws["STATE_CODE"] == "WV"].copy()
pws_wv["POPULATION_SERVED_COUNT"] = pd.to_numeric(
    pws_wv["POPULATION_SERVED_COUNT"], errors="coerce"
)

# Filter to corridor counties (COUNTY_SERVED may have multiple/varied formats)
mask = pws_wv["COUNTY_SERVED"].str.upper().fillna("").apply(
    lambda x: any(c in x for c in CORRIDOR_COUNTIES)
)
corridor_pws = pws_wv[mask].copy()

cols = ["PWSID", "PWS_NAME", "PWS_TYPE_CODE", "PRIMACY_AGENCY_CODE",
        "POPULATION_SERVED_COUNT", "SERVICE_CONNECTIONS_COUNT",
        "COUNTY_SERVED", "CITIES_SERVED", "PWS_ACTIVITY_CODE",
        "PRIMARY_SOURCE_CODE", "OWNER_TYPE_CODE"]
cols = [c for c in cols if c in corridor_pws.columns]
corridor_pws[cols].to_csv("sdwa_corridor_systems.csv", index=False)
print(f"\n{len(corridor_pws)} public water systems in corridor counties")

# --- Small systems (highest vulnerability to demand spikes) ---
small = corridor_pws[corridor_pws["POPULATION_SERVED_COUNT"] < 500]
small[cols].sort_values("POPULATION_SERVED_COUNT").to_csv(
    "sdwa_corridor_small_systems.csv", index=False
)
print(f"{len(small)} systems serve fewer than 500 people")

# --- Violations table, filtered to corridor PWSIDs ---
corridor_ids = set(corridor_pws["PWSID"])
with zf.open("SDWA_VIOLATIONS_ENFORCEMENT.csv") as f:
    viol = pd.read_csv(f, dtype=str, low_memory=False)

viol_corridor = viol[viol["PWSID"].isin(corridor_ids)]
viol_cols = [c for c in ["PWSID", "VIOLATION_ID", "VIOLATION_CODE",
                          "VIOLATION_CATEGORY_CODE", "IS_HEALTH_BASED_IND",
                          "NON_COMPL_PER_BEGIN_DATE", "NON_COMPL_PER_END_DATE",
                          "VIOLATION_STATUS"] if c in viol_corridor.columns]
viol_corridor[viol_cols].to_csv("sdwa_corridor_violations.csv", index=False)
print(f"{len(viol_corridor)} violation records for corridor systems")

print("\nDone. Files written: sdwa_corridor_systems.csv, "
      "sdwa_corridor_small_systems.csv, sdwa_corridor_violations.csv")
