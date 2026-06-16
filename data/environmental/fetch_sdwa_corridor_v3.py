"""
v3: Filters the cached SDWA dataset to Allegheny Trail corridor systems using
two approaches:
  (A) CITY_NAME match against the 28 known corridor towns
  (B) County match via SDWA_GEOGRAPHIC_AREAS.csv (prints schema first since
      the exact area-type coding needs to be confirmed)

REQUIREMENTS:
    pip install pandas

Assumes SDWA_latest_downloads.zip is already in the current directory
(from the v2 script run).
"""

import zipfile
import pandas as pd

LOCAL_ZIP = "SDWA_latest_downloads.zip"
zf = zipfile.ZipFile(LOCAL_ZIP)

# --- Load WV public water systems ---
with zf.open("SDWA_PUB_WATER_SYSTEMS.csv") as f:
    pws = pd.read_csv(f, dtype=str, low_memory=False)

pws["POPULATION_SERVED_COUNT"] = pd.to_numeric(pws["POPULATION_SERVED_COUNT"], errors="coerce")
pws_wv = pws[pws["STATE_CODE"] == "WV"].copy()
print(f"{len(pws_wv)} total WV public water systems")

# =====================================================================
# Approach A: CITY_NAME match against known corridor towns
# =====================================================================
CORRIDOR_TOWNS = [
    "ALBRIGHT", "BRANDONVILLE", "BRUCETON MILLS", "DAVIS", "DURBIN",
    "HAMBLETON", "HARMAN", "HENDRICKS", "HILLSBORO", "KINGWOOD",
    "MARLINTON", "MASONTOWN", "PARSONS", "ROWLESBURG", "TERRA ALTA",
    "THOMAS", "WHITE SULPHUR SPRINGS", "ARBOVALE", "AURORA", "BARTOW",
    "BOWDEN", "CASS", "FRANK", "GREEN BANK", "HUNTERSVILLE",
    "ST. GEORGE", "ST GEORGE", "GLADY",
]

pws_wv["CITY_NAME_UPPER"] = pws_wv["CITY_NAME"].str.upper().fillna("")
city_match = pws_wv[pws_wv["CITY_NAME_UPPER"].isin(CORRIDOR_TOWNS)].copy()
print(f"\nApproach A (CITY_NAME match): {len(city_match)} systems")
print(city_match[["PWSID", "PWS_NAME", "CITY_NAME", "PWS_TYPE_CODE",
                   "OWNER_TYPE_CODE", "POPULATION_SERVED_COUNT",
                   "SERVICE_CONNECTIONS_COUNT", "PWS_ACTIVITY_CODE"]]
      .sort_values("CITY_NAME").to_string(index=False))

city_match.drop(columns=["CITY_NAME_UPPER"]).to_csv(
    "sdwa_corridor_systems_by_city.csv", index=False
)

# =====================================================================
# Approach B: County match via SDWA_GEOGRAPHIC_AREAS.csv
# =====================================================================
with zf.open("SDWA_GEOGRAPHIC_AREAS.csv") as f:
    geo = pd.read_csv(f, dtype=str, low_memory=False, nrows=5)

print("\nColumns in SDWA_GEOGRAPHIC_AREAS.csv:")
for c in geo.columns:
    print("  -", c)

with zf.open("SDWA_GEOGRAPHIC_AREAS.csv") as f:
    geo_full = pd.read_csv(f, dtype=str, low_memory=False)

# Print unique area type codes to understand the schema
area_type_col = next((c for c in geo_full.columns if "AREA_TYPE" in c.upper()), None)
if area_type_col:
    print(f"\nUnique values in {area_type_col}:")
    print(geo_full[area_type_col].value_counts().head(20).to_string())

# Try to find a county-name-like column
county_name_col = next((c for c in geo_full.columns if "NAME" in c.upper()
                         and "AREA" in c.upper()), None) \
                  or next((c for c in geo_full.columns if "COUNTY" in c.upper()), None)
print(f"\nCandidate county-name column: {county_name_col}")

if county_name_col and "PWSID" in geo_full.columns:
    CORRIDOR_COUNTIES = ["PRESTON", "TUCKER", "RANDOLPH", "POCAHONTAS",
                          "GREENBRIER", "MONROE"]
    geo_wv = geo_full.merge(pws_wv[["PWSID"]], on="PWSID")
    county_mask = geo_wv[county_name_col].str.upper().fillna("").apply(
        lambda x: any(c in x for c in CORRIDOR_COUNTIES)
    )
    county_pwsids = set(geo_wv[county_mask]["PWSID"])
    county_match = pws_wv[pws_wv["PWSID"].isin(county_pwsids)].copy()
    print(f"\nApproach B (county match): {len(county_match)} systems")
    county_match.drop(columns=["CITY_NAME_UPPER"], errors="ignore").to_csv(
        "sdwa_corridor_systems_by_county.csv", index=False
    )
else:
    print("\nCould not identify county column in SDWA_GEOGRAPHIC_AREAS.csv "
          "- review printed columns above")

print("\nDone.")
