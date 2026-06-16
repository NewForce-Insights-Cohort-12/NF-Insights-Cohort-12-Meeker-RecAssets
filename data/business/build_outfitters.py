"""
Builds a layer of commercial sporting goods / outfitter businesses relevant
to the Allegheny Trail corridor.

Coordinates are TOWN-CENTER approximations (not geocoded street addresses)
based on the addresses found via web search. Flagged with `in_corridor` to
distinguish the 2 corridor-town businesses (Marlinton, Davis) from the 7
regional-hub businesses (Elkins, Lewisburg, Snowshoe, Richwood) that lie
20-40+ miles outside the 5-mile ALT buffer but are the nearest full-service
outfitters for most of the corridor.

Addresses (from web search):
  Appalachian Sport          - 3 Seneca Trail, Marlinton, WV 24954
  Dirtbean Hale (cafe/bikes)  - 818 2nd Ave, Marlinton, WV 24954
  Blackwater Bikes           - 685 William Ave, Davis, WV 26260
  Driftland Ski & Sport       - 556 William Ave, Davis, WV 26260
  B & J Pawn and Sportshop    - 313 3rd St, Elkins, WV 26241
  Broughton's Sports & Trophy World - 334 Randolph Ave, Elkins, WV 26241
  Dunham's Sports             - 41 Iris Ln, Elkins, WV 26241
  Edward's Sporting Goods     - 158 Beard St, Lewisburg, WV 24901
  Free Spirit Adventures & Bike Sales - Lewisburg, WV 24901 (no street addr found)
  Elk River Snowboard and Ski - 1 Soaring Eagle Dr, Snowshoe, WV 26209
  Four Seasons Outfitters & Adventure Sports - Richwood, WV (no street addr found)
"""

import geopandas as gpd
from shapely.geometry import Point

OUT_DIR = "/home/claude/alt_project/data/business"

# Town-center approximations
MARLINTON = (-80.0967, 38.2306)
DAVIS = (-79.4639, 39.1306)
ELKINS = (-79.8478, 38.9251)
LEWISBURG = (-80.4459, 37.8001)
SNOWSHOE = (-79.9947, 38.4089)
RICHWOOD = (-80.5398, 38.2253)

businesses = [
    {
        "name": "Appalachian Sport",
        "city": "Marlinton, WV",
        "address": "3 Seneca Trail, Marlinton, WV 24954",
        "category": "outfitter_rental",
        "notes": "One-stop outfitter: bike/kayak/canoe rentals, fishing gear, "
                 "shuttles, hunting/outdoor apparel. On the Greenbrier River Trail.",
        "in_corridor": True,
        "geometry": Point(*MARLINTON),
    },
    {
        "name": "Dirtbean Hale (Dirtbean Cafe & Bike Shop)",
        "city": "Marlinton, WV",
        "address": "818 2nd Ave, Marlinton, WV 24954",
        "category": "bike_shop",
        "notes": "Full-service bike shop + cafe; rentals and repairs for the "
                 "Greenbrier River Trail.",
        "in_corridor": True,
        "geometry": Point(*MARLINTON),
    },
    {
        "name": "Blackwater Bikes",
        "city": "Davis, WV",
        "address": "685 William Ave, Davis, WV 26260",
        "category": "bike_shop",
        "notes": "Full-service bike shop since 1983; sales, rentals, repairs. "
                 "Near Section 1/2 of the ALT.",
        "in_corridor": True,
        "geometry": Point(*DAVIS),
    },
    {
        "name": "Driftland Ski & Sport",
        "city": "Davis, WV",
        "address": "556 William Ave, Davis, WV 26260",
        "category": "ski_shop",
        "notes": "Ski/snowboard sales, rentals, and tuning, next to Davis Fire Hall.",
        "in_corridor": True,
        "geometry": Point(*DAVIS),
    },
    {
        "name": "B & J Pawn and Sportshop",
        "city": "Elkins, WV",
        "address": "313 3rd St, Elkins, WV 26241",
        "category": "sporting_goods",
        "notes": "Pawn shop + sporting goods (guns, archery, fishing). "
                 "Regional hub, ~10-15mi from nearest ALT section.",
        "in_corridor": False,
        "geometry": Point(*ELKINS),
    },
    {
        "name": "Broughton's Sports & Trophy World",
        "city": "Elkins, WV",
        "address": "334 Randolph Ave, Elkins, WV 26241",
        "category": "sporting_goods",
        "notes": "Sporting goods, team uniforms, trophies. Regional hub.",
        "in_corridor": False,
        "geometry": Point(*ELKINS),
    },
    {
        "name": "Dunham's Sports",
        "city": "Elkins, WV",
        "address": "41 Iris Ln, Elkins, WV 26241",
        "category": "sporting_goods",
        "notes": "National chain sporting goods store. Regional hub.",
        "in_corridor": False,
        "geometry": Point(*ELKINS),
    },
    {
        "name": "Edward's Sporting Goods",
        "city": "Lewisburg, WV",
        "address": "158 Beard St, Lewisburg, WV 24901",
        "category": "sporting_goods",
        "notes": "Sporting goods incl. guns/knives. Regional hub near Section 4 "
                 "roadwalk and southern GRT terminus.",
        "in_corridor": False,
        "geometry": Point(*LEWISBURG),
    },
    {
        "name": "Free Spirit Adventures & Bike Sales",
        "city": "Lewisburg, WV",
        "address": "Lewisburg, WV 24901 (exact address not found)",
        "category": "bike_shop",
        "notes": "Bike shop, rentals/sales/repairs, on the Greenbrier River Trail.",
        "in_corridor": False,
        "geometry": Point(*LEWISBURG),
    },
    {
        "name": "Elk River Snowboard and Ski",
        "city": "Snowshoe, WV",
        "address": "1 Soaring Eagle Dr, Snowshoe, WV 26209",
        "category": "ski_shop",
        "notes": "Ski/snowboard rental & retail at Snowshoe Mountain Resort "
                 "(Soaring Eagle Lodge); second 'valley shop' location in "
                 "Slatyfork. ~20mi from Marlinton/ALT.",
        "in_corridor": False,
        "geometry": Point(*SNOWSHOE),
    },
    {
        "name": "Four Seasons Outfitters & Adventure Sports",
        "city": "Richwood, WV",
        "address": "Richwood, WV (exact address not found)",
        "category": "outfitter_rental",
        "notes": "Bike shop / outdoor outfitter. Regional hub south of the "
                 "corridor (Cranberry Glades/Highland Scenic Hwy area).",
        "in_corridor": False,
        "geometry": Point(*RICHWOOD),
    },
]

gdf = gpd.GeoDataFrame(businesses, crs="EPSG:4326")
gdf["data_quality"] = "town-center approximation, not geocoded street address"

gdf.to_file(f"{OUT_DIR}/outfitter_businesses.geojson", driver="GeoJSON")

print(f"Wrote {len(gdf)} outfitter/sporting goods businesses")
print(f"  In corridor (Marlinton/Davis): {gdf['in_corridor'].sum()}")
print(f"  Regional hubs (Elkins/Lewisburg/Snowshoe/Richwood): {(~gdf['in_corridor']).sum()}")
print("\n", gdf[["name","city","category","in_corridor"]].to_string(index=False))
