"""
Builds the core analytical artifact for the "Recreation assets, public lands,
and community/environmental capacity" piece of the ALT-EXP project:

  Where do recreation assets create OPPORTUNITY, and where might tourism
  create PRESSURE?

Produces a per-town scorecard (town_scorecard.csv) joining:
  - Business density (existing tourism-economy baseline)
  - Public water system capacity indicators (TNCWS count, CWS pop/connection
    ratio, small/vulnerable system count)
  - Recreation asset proximity (named state parks/forests/USFS sites,
    GRT access)
  - Outfitter/commercial recreation access (in-corridor vs. none)
  - Karst geology overlap (WVGES 1968 karst-formations layer, sourced via DOE
    EDX) - towns sitting on mapped karst are at elevated groundwater
    contamination risk from private wells + private septic systems, which
    compounds water-capacity pressure with a real environmental dimension

Each town gets an OPPORTUNITY score (recreation assets + existing commercial
base = readiness to capture more visitor spending) and a PRESSURE score
(small/concentrated water systems + thin existing business base + karst
exposure = limited capacity to absorb growth, with environmental risk) - NOT
combined into one number, since the analytical point is that these are two
different axes a town can score high or low on independently.

OUTPUT: data/town_scorecard.csv
"""

import pandas as pd
import geopandas as gpd

BASE = "/home/claude/alt_project"
OUT = "/home/claude/recreation_capacity/data"
KARST_SHP = "/home/claude/recreation_capacity/data/environmental/karst/geologyKarstFormations_WVGES_1968_ll83.shp"

# --- Load source data ---
biz = pd.read_csv(f"{BASE}/data/business/trail_corridor_business_totals.csv")
sdwa = pd.read_csv(f"{BASE}/data/environmental/sdwa_corridor_systems_clean.csv")
outfitters = gpd.read_file(f"{BASE}/data/business/outfitter_businesses.geojson")
lands = gpd.read_file(f"{BASE}/data/recreation/public_recreation_lands.geojson")
amenities = gpd.read_file(f"{BASE}/data/recreation/public_recreation_amenities.geojson")
places_inc = gpd.read_file(f"{BASE}/data/boundaries/incorporated_place.geojson")
places_cdp = gpd.read_file(f"{BASE}/data/boundaries/census_designated_place.geojson")
karst = gpd.read_file(KARST_SHP).to_crs("EPSG:4326")
karst_union = karst.geometry.union_all()

# --- Normalize town names ---
def clean_town(namelsad):
    for suffix in [" city", " town", " CDP"]:
        namelsad = namelsad.replace(suffix, "")
    return namelsad.strip()

biz["town"] = biz["NAMELSAD"].apply(clean_town)
biz["town_upper"] = biz["town"].str.upper().str.replace(".", "", regex=False)

# --- SDWA aggregation per town ---
sdwa_agg = sdwa.groupby("CITY_NAME").agg(
    pws_total_count=("PWSID", "count"),
    pws_tncws_count=("PWS_TYPE_CODE", lambda x: (x == "TNCWS").sum()),
    pws_cws_count=("PWS_TYPE_CODE", lambda x: (x == "CWS").sum()),
    pws_small_count=("POPULATION_SERVED_COUNT", lambda x: (x < 100).sum()),
).reset_index()

# Municipal (CWS, owner=L) capacity ratio - pop served per connection
cws_local = sdwa[(sdwa["PWS_TYPE_CODE"] == "CWS") & (sdwa["OWNER_TYPE_CODE"] == "L")].copy()
cws_local["ratio"] = cws_local["POPULATION_SERVED_COUNT"] / cws_local["SERVICE_CONNECTIONS_COUNT"].replace(0, pd.NA)
cws_agg = cws_local.groupby("CITY_NAME").agg(
    municipal_pop_served=("POPULATION_SERVED_COUNT", "sum"),
    municipal_connections=("SERVICE_CONNECTIONS_COUNT", "sum"),
).reset_index()
cws_agg["municipal_pop_per_connection"] = (
    cws_agg["municipal_pop_served"] / cws_agg["municipal_connections"]
).round(2)

sdwa_agg = sdwa_agg.merge(cws_agg[["CITY_NAME", "municipal_pop_served",
                                     "municipal_connections", "municipal_pop_per_connection"]],
                           on="CITY_NAME", how="left")

# --- Outfitters per town ---
outfitter_counts = outfitters[outfitters["in_corridor"]].groupby("city").size()
outfitter_counts.index = outfitter_counts.index.str.replace(", WV", "", regex=False).str.upper()

# --- Recreation asset proximity (recreation lands within ~10mi of town, by name match heuristic) ---
# Hand-mapped from earlier project analysis: which corridor towns sit at/near
# which major recreation assets (state parks/forests/USFS/observatory).
RECREATION_NEAR_TOWN = {
    "DAVIS": ["Blackwater Falls State Park", "Canaan Valley Resort State Park"],
    "AURORA": ["Cathedral State Park"],
    "BRUCETON MILLS": ["Cooper's Rock State Forest (near, unmapped)", "Chestnut Ridge Park (near, unmapped)"],
    "PARSONS": ["Monongahela NF - Otter Creek/Spruce Knob area (near)"],
    "MARLINTON": ["Watoga State Park", "Beartown State Park", "Droop Mountain Battlefield SP",
                   "Greenbrier River Trail (direct connection)"],
    "HILLSBORO": ["Droop Mountain Battlefield State Park"],
    "CASS": ["Cass Scenic Railroad State Park", "Greenbrier River Trail (terminus)"],
    "GREEN BANK": ["Green Bank Observatory"],
    "DURBIN": ["Monongahela NF (Cheat Mountain area)"],
    "WHITE SULPHUR SPRINGS": ["Greenbrier Resort (self-supplied, not public rec)"],
}

# --- Karst geology: does this town sit on (or very near) mapped karst? ---
def town_karst_status(town_name, geo_level, near_threshold_mi=1.0):
    """Returns (on_karst: bool, dist_mi: float or None)."""
    target = town_name.upper().replace(".", "")
    df = places_inc if geo_level == "incorporated_place" else places_cdp
    matches = df[df["NAMELSAD"].str.upper().str.replace(".", "", regex=False)
                 .str.contains(target, na=False)]
    if len(matches) == 0:
        return False, None
    geom = matches.geometry.iloc[0]
    on_karst = geom.intersects(karst_union)
    geom_proj = gpd.GeoSeries([geom], crs="EPSG:4326").to_crs("EPSG:26917").iloc[0]
    karst_proj = gpd.GeoSeries([karst_union], crs="EPSG:4326").to_crs("EPSG:26917").iloc[0]
    dist_mi = round(geom_proj.distance(karst_proj) / 1609.34, 2)
    return on_karst, dist_mi

# --- Assemble scorecard ---
rows = []
for _, r in biz.iterrows():
    town = r["town_upper"]
    sdwa_row = sdwa_agg[sdwa_agg["CITY_NAME"] == town]
    rec_assets = RECREATION_NEAR_TOWN.get(town, [])
    n_outfitters = outfitter_counts.get(town, 0)
    on_karst, karst_dist_mi = town_karst_status(r["town"], r["geography_level"])

    row = {
        "town": r["town"],
        "geography_level": r["geography_level"],
        "total_business_count": r["total_business_count"],
        "businesses_per_sq_mi": r["businesses_per_sq_mi"],
        "recreation_assets_nearby": len(rec_assets),
        "recreation_asset_names": "; ".join(rec_assets) if rec_assets else "none mapped",
        "outfitters_in_town": n_outfitters,
        "pws_total_count": int(sdwa_row["pws_total_count"].iloc[0]) if len(sdwa_row) else 0,
        "pws_tncws_count": int(sdwa_row["pws_tncws_count"].iloc[0]) if len(sdwa_row) else 0,
        "pws_small_systems_under_100pop": int(sdwa_row["pws_small_count"].iloc[0]) if len(sdwa_row) else 0,
        "municipal_pop_per_connection": (
            sdwa_row["municipal_pop_per_connection"].iloc[0] if len(sdwa_row) and pd.notna(sdwa_row["municipal_pop_per_connection"].iloc[0]) else None
        ),
        "has_municipal_cws": len(sdwa_row) > 0 and pd.notna(sdwa_row["municipal_pop_per_connection"].iloc[0]),
        "on_karst": on_karst,
        "dist_to_karst_mi": karst_dist_mi,
    }
    rows.append(row)

df = pd.DataFrame(rows)

# --- Scoring ---
# OPPORTUNITY: recreation assets nearby + outfitter presence + existing
# business density (proxy for whether the town already has infrastructure
# to build on). Simple additive score, not normalized to a fixed scale -
# meant for relative ranking within this corridor, not absolute benchmarking.
df["opportunity_score"] = (
    df["recreation_assets_nearby"] * 2
    + (df["outfitters_in_town"] > 0).astype(int) * 2
    + pd.cut(df["businesses_per_sq_mi"], bins=[-1, 10, 30, 60, 1000], labels=[0, 1, 2, 3]).astype(int)
)

# PRESSURE: many small/transient water systems (fragmented capacity, no
# municipal backbone) + no municipal CWS at all (no central system to lean
# on for growth) + very thin existing business base (limited absorption
# capacity / no slack) + sitting on mapped karst (groundwater contamination
# risk from private wells/septic, compounding the water-capacity concern
# with a real environmental one). Higher = more exposed to tourism-driven
# stress.
df["pressure_score"] = (
    (df["pws_small_systems_under_100pop"] >= 3).astype(int) * 2
    + (~df["has_municipal_cws"]).astype(int) * 2
    + (df["total_business_count"] < 10).astype(int) * 1
    + df["on_karst"].astype(int) * 2
)

df = df.sort_values(["opportunity_score", "pressure_score"], ascending=[False, False])
df.to_csv(f"{OUT}/town_scorecard.csv", index=False)

print(f"Wrote {len(df)}-town scorecard")
print(df[["town", "opportunity_score", "pressure_score", "recreation_assets_nearby",
           "outfitters_in_town", "pws_small_systems_under_100pop", "has_municipal_cws",
           "on_karst", "total_business_count"]].to_string(index=False))
