"""
Compares sdwa_corridor_systems_by_city.csv (Approach A) against
sdwa_corridor_systems_by_county.csv (Approach B) to surface systems that
the county-based match catches but the city-based match did not -
i.e. systems registered under a city name other than the 28 known corridor
towns, but still located in a corridor county.

REQUIREMENTS:
    pip install pandas

Run in the same directory as the two CSVs produced by v3.
"""

import pandas as pd

city_df = pd.read_csv("sdwa_corridor_systems_by_city.csv", dtype=str, low_memory=False)
county_df = pd.read_csv("sdwa_corridor_systems_by_county.csv", dtype=str, low_memory=False)

city_df["POPULATION_SERVED_COUNT"] = pd.to_numeric(city_df["POPULATION_SERVED_COUNT"], errors="coerce")
county_df["POPULATION_SERVED_COUNT"] = pd.to_numeric(county_df["POPULATION_SERVED_COUNT"], errors="coerce")

city_ids = set(city_df["PWSID"])
county_ids = set(county_df["PWSID"])

only_county = county_df[county_df["PWSID"].isin(county_ids - city_ids)].copy()
only_city = city_df[city_df["PWSID"].isin(city_ids - county_ids)].copy()
both = city_ids & county_ids

print(f"City-based match: {len(city_ids)} systems")
print(f"County-based match: {len(county_ids)} systems")
print(f"In both: {len(both)}")
print(f"Only in county match (different city name, corridor county): {len(only_county)}")
print(f"Only in city match (corridor town, but county field didn't match): {len(only_city)}")

# --- What cities appear in the county-only set? ---
print("\n=== Cities/towns appearing in county-match but NOT in our corridor-town list ===")
print(only_county["CITY_NAME"].value_counts().to_string())

# --- Active community water systems only, for a cleaner read ---
print("\n=== County-only matches: active CWS (community systems) ===")
active_cws = only_county[
    (only_county["PWS_TYPE_CODE"] == "CWS") &
    (only_county["PWS_ACTIVITY_CODE"] == "A")
]
cols = ["PWSID", "PWS_NAME", "CITY_NAME", "OWNER_TYPE_CODE",
        "POPULATION_SERVED_COUNT", "SERVICE_CONNECTIONS_COUNT"]
print(active_cws[cols].sort_values("CITY_NAME").to_string(index=False))

# --- Any city-match systems NOT picked up by county match (potential gaps in COUNTY_SERVED data) ---
print(f"\n=== City-match systems NOT in county match ({len(only_city)}) ===")
if len(only_city):
    print(only_city[["PWSID","PWS_NAME","CITY_NAME","PWS_TYPE_CODE","PWS_ACTIVITY_CODE"]]
          .sort_values("CITY_NAME").to_string(index=False))
