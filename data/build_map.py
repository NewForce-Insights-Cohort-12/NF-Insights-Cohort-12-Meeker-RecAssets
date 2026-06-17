"""
Rebuild recreation_capacity_map.html with updated inventory:
  - 23 public recreation lands (was 14) — added Cooper's Rock, Cheat Canyon WMA,
    Canaan Valley NWR, Dolly Sods, Otter Creek, Laurel Fork N/S, Spruce Knob-Seneca
    Rocks NRA, Cranberry Wilderness
  - 4 private/commercial facilities (new layer) — Snowshoe Mountain Resort,
    Elk River Touring Center, The Greenbrier Resort, Chestnut Ridge Regional Park
  - Updated town scorecard with revised opportunity scores
"""

from pathlib import Path
import folium
import geopandas as gpd
import pandas as pd
from branca.colormap import LinearColormap

RC   = Path("/sessions/funny-kind-knuth/mnt/recreation_capacity")
DATA = RC / "data"
OUT  = RC / "outputs"
OUT.mkdir(exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
trail      = gpd.read_file(DATA / "trail" / "allegheny_trail_master_route.geojson")
corridor   = gpd.read_file(DATA / "trail" / "alt_corridor_5mi_v2.geojson")
waypoints  = gpd.read_file(DATA / "trail" / "alt_waypoints.geojson")

places_inc = gpd.read_file(DATA / "boundaries" / "incorporated_place.geojson")
places_cdp = gpd.read_file(DATA / "boundaries" / "census_designated_place.geojson")

lands      = gpd.read_file(DATA / "recreation" / "public_recreation_lands.geojson")
amenities  = gpd.read_file(DATA / "recreation" / "public_recreation_amenities.geojson")
private    = gpd.read_file(DATA / "recreation" / "private_recreation_facilities.geojson")
outfitters = gpd.read_file(DATA / "business"   / "outfitter_businesses.geojson")

grt_cl     = gpd.read_file(DATA / "recreation" / "greenbrier_river_trail_centerline.geojson")
grt_water  = gpd.read_file(DATA / "recreation" / "greenbrier_river_trail_water.geojson")
grt_amen   = gpd.read_file(DATA / "recreation" / "greenbrier_river_trail_amenities.geojson")

karst      = gpd.read_file(DATA / "environmental" / "karst" / "karst_corridor_clip.geojson")
scorecard  = pd.read_csv(DATA / "town_scorecard.csv")
sdwa       = pd.read_csv(DATA / "environmental" / "sdwa_corridor_systems_clean.csv")

print(f"Public lands: {len(lands)}  |  Private facilities: {len(private)}")
print(f"Amenities: {len(amenities)}  |  Outfitters: {len(outfitters)}")
print(f"Scorecard: {len(scorecard)} towns  |  Karst polygons: {len(karst)}")

# ── Join scorecard to geometries ───────────────────────────────────────────────
def match_geometry(town_name, geo_level):
    target = town_name.upper().replace(".", "")
    df = places_inc if geo_level == "incorporated_place" else places_cdp
    m = df[df["NAMELSAD"].str.upper().str.replace(".", "", regex=False).str.contains(target, na=False)]
    return m.geometry.iloc[0] if len(m) else None

scorecard["geometry"] = scorecard.apply(
    lambda r: match_geometry(r["town"], r["geography_level"]), axis=1
)
scorecard_gdf = gpd.GeoDataFrame(
    scorecard[scorecard["geometry"].notna()], geometry="geometry", crs="EPSG:4326"
)

# ── Map ────────────────────────────────────────────────────────────────────────
m = folium.Map(location=[38.8, -79.85], zoom_start=8, tiles="CartoDB positron")
folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)

# 1. Corridor + trail route
folium.GeoJson(
    corridor,
    name="5-mile analysis corridor",
    style_function=lambda x: {"fillColor": "#cccccc", "color": "#999999",
                               "weight": 1, "fillOpacity": 0.08},
).add_to(m)

trail_layer = folium.FeatureGroup(name="Allegheny Trail route")
for geom in trail.geometry:
    parts = geom.geoms if hasattr(geom, "geoms") else [geom]
    for part in parts:
        coords = [(lat, lon) for lon, lat in part.coords]
        folium.PolyLine(coords, color="#e8a735", weight=3, opacity=0.85,
                        tooltip="Allegheny Trail").add_to(trail_layer)
trail_layer.add_to(m)

# 2. Opportunity choropleth
opp_max = max(scorecard_gdf["opportunity_score"].max(), 1)
opp_colormap = LinearColormap(["#f7fcf5", "#74c476", "#005a32"], vmin=0, vmax=opp_max)

opp_layer = folium.FeatureGroup(name="Towns: OPPORTUNITY score (v3 — expanded inventory)")
for _, row in scorecard_gdf.iterrows():
    popup_html = (
        f"<b>{row['town']}</b><br>"
        f"<b>Opportunity: {row['opportunity_score']}</b>"
        f"<br>Recreation assets nearby: {row['recreation_assets_nearby']}"
        f"<br><i style='font-size:11px'>{row['recreation_asset_names']}</i>"
        f"<br>Outfitters in town: {row['outfitters_in_town']}"
        f"<br>Total businesses: {row['total_business_count']}"
    )
    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=lambda x, c=opp_colormap(row["opportunity_score"]): {
            "fillColor": c, "color": "#444", "weight": 1, "fillOpacity": 0.7,
        },
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"{row['town']}: Opportunity {row['opportunity_score']}",
    ).add_to(opp_layer)
opp_layer.add_to(m)
opp_colormap.caption = "Opportunity score"
opp_colormap.add_to(m)

# 3. Pressure choropleth (off by default)
press_max = max(scorecard_gdf["pressure_score"].max(), 1)
press_colormap = LinearColormap(["#fff5f0", "#fb6a4a", "#a50f15"], vmin=0, vmax=press_max)

press_layer = folium.FeatureGroup(
    name="Towns: PRESSURE score (fragmented water + karst)", show=False
)
for _, row in scorecard_gdf.iterrows():
    cws_note = (f"{row['municipal_pop_per_connection']:.2f} pop/connection"
                if row["has_municipal_cws"] and pd.notna(row["municipal_pop_per_connection"])
                else "No municipal CWS")
    popup_html = (
        f"<b>{row['town']}</b><br>"
        f"<b>Pressure: {row['pressure_score']}</b>"
        f"<br>Small water systems (<100 pop): {row['pws_small_systems_under_100pop']}"
        f"<br>Municipal CWS: {'Yes — ' + cws_note if row['has_municipal_cws'] else 'None'}"
        f"<br>On karst: {'Yes' if row['on_karst'] else 'No'} ({row['dist_to_karst_mi']:.2f} mi)"
        f"<br>Businesses: {row['total_business_count']}"
    )
    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=lambda x, c=press_colormap(row["pressure_score"]): {
            "fillColor": c, "color": "#444", "weight": 1, "fillOpacity": 0.7,
        },
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['town']}: Pressure {row['pressure_score']}",
    ).add_to(press_layer)
press_layer.add_to(m)

# 4. Karst geology
karst_layer = folium.FeatureGroup(name="Karst geology (WVGES 1968)", show=False)
folium.GeoJson(
    karst,
    style_function=lambda x: {"fillColor": "#f6d860", "color": "#c9a227",
                               "weight": 1, "fillOpacity": 0.35},
    tooltip="Mapped karst (WVGES 1968 — generalized)",
).add_to(karst_layer)
karst_layer.add_to(m)

# 5. Public recreation lands — expanded icon set
FACILITY_ICONS = {
    "state_park":                    ("green",     "tree"),
    "state_forest":                  ("darkgreen", "tree"),
    "wildlife_management_area":      ("darkgreen", "paw"),
    "national_wildlife_refuge":      ("darkblue",  "dove"),
    "national_forest_wilderness":    ("green",     "mountain"),
    "national_forest_scenic_area":   ("green",     "leaf"),
    "national_forest_recreation_area": ("green",   "tint"),
    "national_recreation_area":      ("blue",      "sun"),
    "federal_research_facility":     ("darkblue",  "wifi"),
}

rec_lands_layer = folium.FeatureGroup(name="Public recreation lands (parks / forests / USFS / refuges / wilderness)")
for _, row in lands.iterrows():
    color, icon = FACILITY_ICONS.get(row["facility_type"], ("gray", "info-sign"))
    in_corridor_note = "" if "outside" not in str(row.get("data_quality","")) else \
        f"<br><i>({row['data_quality']})</i>"
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"<i>{row['facility_type'].replace('_',' ').title()}</i><br>"
        f"{row['agency']}<br>{row['notes']}"
        f"{in_corridor_note}"
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon=icon, prefix="fa"),
    ).add_to(rec_lands_layer)
rec_lands_layer.add_to(m)

# 6. Private / commercial recreation facilities (NEW LAYER)
PRIVATE_ICONS = {
    "ski_mountain_resort":  ("red",      "skiing"),
    "eco_lodge_outfitter":  ("orange",   "hiking"),
    "destination_resort":   ("red",      "hotel"),
    "county_park":          ("cadetblue","tree"),
}

private_layer = folium.FeatureGroup(
    name="Private & commercial recreation facilities (resorts / lodges)"
)
for _, row in private.iterrows():
    color, icon = PRIVATE_ICONS.get(row["facility_type"], ("red", "star"))
    # Fall back to FontAwesome icons that exist
    icon_map = {
        "skiing": "snowflake", "hiking": "male", "hotel": "building",
        "tree": "tree", "star": "star"
    }
    fa_icon = icon_map.get(icon, "star")
    in_corr = row.get("in_corridor", False)
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"<i>{row['facility_type'].replace('_',' ').title()} — {'In corridor' if in_corr else 'Near corridor'}</i><br>"
        f"{row['agency']}<br>{row['notes']}"
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"[Private] {row['name']}",
        icon=folium.Icon(color=color, icon=fa_icon, prefix="fa"),
    ).add_to(private_layer)
private_layer.add_to(m)

# 7. Recreation amenities
AMENITY_ICONS = {
    "campground":     ("orange",     "campground"),
    "picnic_area":    ("cadetblue",  "utensils"),
    "scenic_overlook":("purple",     "eye"),
}
amenity_layer = folium.FeatureGroup(name="Recreation amenities (camping / picnic / overlooks)", show=False)
for _, row in amenities.iterrows():
    color, icon = AMENITY_ICONS.get(row["amenity_type"], ("gray", "info"))
    fa_icon_map = {"campground": "tree", "utensils": "cutlery", "eye": "eye"}
    fa_icon = fa_icon_map.get(icon, "info")
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"{row['amenity_type'].replace('_',' ').title()}<br>"
        f"{row['associated_facility']}<br>{row['notes']}"
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon=fa_icon, prefix="fa"),
    ).add_to(amenity_layer)
amenity_layer.add_to(m)

# 8. Water systems
water_layer = folium.FeatureGroup(name="Municipal water systems (capacity context)", show=False)
cws_municipal = sdwa[(sdwa["PWS_TYPE_CODE"] == "CWS") & (sdwa["OWNER_TYPE_CODE"] == "L")]
for _, row in scorecard_gdf.iterrows():
    town_upper = row["town"].upper().replace(".", "")
    town_cws = cws_municipal[cws_municipal["CITY_NAME"] == town_upper]
    if len(town_cws) == 0:
        continue
    total_pop = town_cws["POPULATION_SERVED_COUNT"].sum()
    total_conn = town_cws["SERVICE_CONNECTIONS_COUNT"].sum()
    centroid = row.geometry.centroid
    popup_html = (
        f"<b>{row['town']} — Municipal CWS</b><br>"
        f"Systems: {len(town_cws)}<br>"
        f"Pop served: {int(total_pop):,}<br>"
        f"Connections: {int(total_conn):,}<br>"
        f"Pop/connection: {row['municipal_pop_per_connection']:.2f}"
    )
    folium.CircleMarker(
        location=[centroid.y, centroid.x],
        radius=max(4, min(total_pop / 200, 20)),
        color="#1a6faf", fill=True, fill_color="#4ea8de", fill_opacity=0.6,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{row['town']}: {int(total_pop):,} pop served",
    ).add_to(water_layer)
water_layer.add_to(m)

# 9. Outfitters
outfitter_layer = folium.FeatureGroup(name="Outfitters & sporting goods businesses")
for _, row in outfitters.iterrows():
    color = "darkgreen" if row["in_corridor"] else "cadetblue"
    popup_html = (
        f"<b>{row['name']}</b><br>{row['address']}<br>{row['notes']}<hr style='margin:4px 0'>"
        f"<i>{'Within ALT corridor' if row['in_corridor'] else 'Regional hub (outside 5-mile corridor)'}</i>"
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon="shopping-cart", prefix="fa"),
    ).add_to(outfitter_layer)
outfitter_layer.add_to(m)

# 10. Greenbrier River Trail
grt_line_layer = folium.FeatureGroup(name="Greenbrier River Trail route (comparison)", show=False)
coords = [(lat, lon) for lon, lat in grt_cl.geometry.iloc[0].coords]
folium.PolyLine(coords, color="#3186cc", weight=3, opacity=0.6, dash_array="8,6",
                tooltip="Greenbrier River Trail").add_to(grt_line_layer)
grt_line_layer.add_to(m)

grt_water_layer = folium.FeatureGroup(name="GRT water access (comparison)", show=False)
for _, row in grt_water.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5, color="#3186cc", fill=True, fill_color="#3186cc", fill_opacity=0.7,
        tooltip=row.get("name", "Water access"),
    ).add_to(grt_water_layer)
grt_water_layer.add_to(m)

grt_amen_layer = folium.FeatureGroup(name="GRT amenities (comparison)", show=False)
for _, row in grt_amen.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4, color="#1a6faf", fill=True, fill_color="#a3cde8", fill_opacity=0.8,
        tooltip=row.get("name", "Amenity"),
    ).add_to(grt_amen_layer)
grt_amen_layer.add_to(m)
grt_water_layer.add_to(m)
grt_amen_layer.add_to(m)

# 11. ALT waypoints
wp_layer = folium.FeatureGroup(name="ALT waypoints / trailheads", show=False)
for _, row in waypoints.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4, color="#e8a735", fill=True, fill_color="#fff5cc", fill_opacity=0.9,
        tooltip=row.get("name", "Waypoint"),
        popup=folium.Popup(str(row.get("name", "")) + "<br>" + str(row.get("notes", "")), max_width=240),
    ).add_to(wp_layer)
wp_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
out_path = OUT / "recreation_capacity_map.html"
m.save(str(out_path))
print(f"\nSaved → {out_path}")
print(f"Public lands: {len(lands)} features across {lands['facility_type'].nunique()} facility types")
print(f"Private facilities: {len(private)} features")
print(f"Amenities: {len(amenities)}  |  Outfitters: {len(outfitters)}")
