"""
Joins the cleaned SDWA corridor water systems dataset to the existing
recreation lands/amenities GeoJSON layers, attaching aggregated water-system
info (count, population served, connections, system names) as new properties
on matched features.

Also identifies SDWA recreation-related systems that DON'T match any existing
feature - these are candidates for future additions (printed at the end, not
auto-added since they lack coordinates).

OUTPUT (overwrites in place):
  data/recreation/public_recreation_lands.geojson      (+water_system_* fields)
  data/recreation/public_recreation_amenities.geojson  (+water_system_* fields)
"""

import pandas as pd
import geopandas as gpd

BASE = "/home/claude/alt_project"
sdwa = pd.read_csv(f"{BASE}/data/environmental/sdwa_corridor_systems_clean.csv")
lands = gpd.read_file(f"{BASE}/data/recreation/public_recreation_lands.geojson")
amenities = gpd.read_file(f"{BASE}/data/recreation/public_recreation_amenities.geojson")

# Mapping: (match function on PWS_NAME) -> (dataframe, feature 'name' value)
def starts(prefix):
    return lambda n: n.upper().startswith(prefix)

def equals(name):
    return lambda n: n.upper() == name

MATCHES = [
    (equals("CATHEDRAL STATE PARK"), lands, "Cathedral State Park"),
    (equals("CASS SCENIC RAILROAD"), lands, "Cass Scenic Railroad State Park"),
    (equals("CANAAN VALLEY STATE PARK"), lands, "Canaan Valley Resort State Park"),
    (equals("BLACKWATER FALLS STATE PARK"), lands, "Blackwater Falls State Park"),
    (equals("BEAR TOWN STATE PARK - HP"), lands, "Beartown State Park"),
    (equals("DROOP MOUNTAIN BATTLEFIELD STATE PARK"), lands, "Droop Mountain Battlefield State Park"),
    (equals("NATIONAL RADIO ASTRONOMY OBSERVATORY"), lands, "Green Bank Observatory"),
    (starts("WATOGA STATE PARK"), amenities, "Watoga State Park Campground"),
    (starts("LAKE SHERWOOD"), amenities, "Lake Sherwood Campground"),
]

# Track which SDWA rows got matched
matched_idx = set()
agg = {}  # (df_id, feature_name) -> list of row dicts

for idx, row in sdwa.iterrows():
    name = row["PWS_NAME"]
    for matchfn, df, feature_name in MATCHES:
        if matchfn(name):
            key = (id(df), feature_name)
            agg.setdefault(key, []).append(row)
            matched_idx.add(idx)
            break

# Apply aggregates to the geodataframes
for (df_id, feature_name), rows in agg.items():
    df = lands if df_id == id(lands) else amenities
    sub = pd.DataFrame(rows)
    total_pop = int(sub["POPULATION_SERVED_COUNT"].sum())
    total_conn = int(sub["SERVICE_CONNECTIONS_COUNT"].sum())
    names = "; ".join(sub["PWS_NAME"] + " (" + sub["PWS_TYPE_CODE"] + ")")

    mask = df["name"] == feature_name
    if not mask.any():
        print(f"WARNING: feature '{feature_name}' not found in target layer")
        continue

    df.loc[mask, "water_system_count"] = len(sub)
    df.loc[mask, "water_system_pop_served"] = total_pop
    df.loc[mask, "water_system_connections"] = total_conn
    df.loc[mask, "water_system_names"] = names

# Save updated layers
lands.to_file(f"{BASE}/data/recreation/public_recreation_lands.geojson", driver="GeoJSON")
amenities.to_file(f"{BASE}/data/recreation/public_recreation_amenities.geojson", driver="GeoJSON")

print(f"Matched {len(matched_idx)} of {len(sdwa)} SDWA systems to existing recreation features")
print("\nMatched features:")
for (df_id, feature_name), rows in agg.items():
    layer = "lands" if df_id == id(lands) else "amenities"
    sub = pd.DataFrame(rows)
    print(f"  [{layer}] {feature_name}: {len(sub)} systems, "
          f"pop_served={int(sub['POPULATION_SERVED_COUNT'].sum())}, "
          f"connections={int(sub['SERVICE_CONNECTIONS_COUNT'].sum())}")

# --- Unmatched recreation-related systems (candidates for future additions) ---
unmatched = sdwa[~sdwa.index.isin(matched_idx)]
keywords = ["USFS", "STATE FOREST", "STATE PARK", "WILDLIFE MANAGEMENT", "GREENBRIER RIVER TRAIL",
            "COOPERS ROCK", "CHESTNUT RIDGE", "BERWIND LAKE"]
candidates = unmatched[unmatched["PWS_NAME"].str.upper().apply(
    lambda x: any(k in x for k in keywords)
)]
print(f"\n{len(candidates)} unmatched recreation-related systems "
      f"(candidates for future map additions - no coordinates available from SDWIS):")
for _, r in candidates.iterrows():
    print(f"  {r['PWS_NAME']:45s} | {r['CITY_NAME']:20s} | pop={r['POPULATION_SERVED_COUNT']}")
