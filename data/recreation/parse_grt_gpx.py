"""
Parses the user-provided Greenbrier River Trail GPX
(GreenbrierRiverTrailWV-.gpx, from gpx.studio) into:

  1. greenbrier_river_trail_centerline.geojson - the actual surveyed trail
     route (1917 track points, ~78.8mi vs official 77.1mi - replaces the
     v1 approximate centerline built from named-community anchors)

  2. greenbrier_river_trail_water.geojson - REPLACES the v2 interpolated
     water-access layer with REAL water/well-pump locations from the GPX
     waypoints (6 found: MM 9.5, 25, 28.5, 55.1, 63.8, 69.6 - more than the
     5 SDWA-derived points, and at verified on-trail positions)

  3. greenbrier_river_trail_amenities.geojson - other trail amenities:
     shelters/campsites, bathrooms, bike repair stations, picnic areas,
     trailhead parking, tunnels/bridges

Waypoint name patterns observed: "<mile> <Description>" (e.g. "9.5 Campsite/
Shelter", "55.1 Water"). Some have no mile prefix (named landmarks/businesses).
"""

import re
import gpxpy
import geopandas as gpd
from shapely.geometry import LineString, Point

GPX_PATH = "/home/claude/alt_project/data/recreation/source_gpx/GreenbrierRiverTrailWV-.gpx"
OUT_DIR = "/home/claude/alt_project/data/recreation"

with open(GPX_PATH) as f:
    gpx = gpxpy.parse(f)

# --- 1. Centerline from track ---
track_points = []
for track in gpx.tracks:
    for seg in track.segments:
        for pt in seg.points:
            track_points.append((pt.longitude, pt.latitude))

line = LineString(track_points)
gdf_line = gpd.GeoDataFrame([{
    "name": "Greenbrier River Trail",
    "length_mi_official": 77.1,
    "length_mi_gpx": round(
        gpd.GeoSeries([line], crs="EPSG:4326").to_crs("EPSG:26917").iloc[0].length / 1609.34, 1
    ),
    "source": "User-supplied GPX (gpx.studio), GreenbrierRiverTrailWV-.gpx",
    "geometry": line,
}], crs="EPSG:4326")
gdf_line.to_file(f"{OUT_DIR}/greenbrier_river_trail_centerline.geojson", driver="GeoJSON")
print(f"Centerline: {len(track_points)} points, "
      f"{gdf_line['length_mi_gpx'].iloc[0]}mi (official 77.1mi)")

# --- 2 & 3. Classify waypoints ---
MILE_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(.*)$")

water_kw = ["water", "well pump", "fountain"]
bathroom_kw = ["bathroom"]
shelter_kw = ["camp", "shelter"]
repair_kw = ["bike repair"]
picnic_kw = ["picnic"]
parking_kw = ["parking", "trailhead", "trail access", "boat launch"]
landmark_kw = ["tunnel", "bridge", "depot", "station"]
business_kw = ["cafe", "lodge", "grill", "subway", "store", "market", "sport",
                "bikes", "cottages", "cabins", "campground", "the greenbrier",
                "trading post", "co-op", "golf club", "medical", "cvb",
                "rivertown", "alfredo", "dari land", "dirtbean", "dirt bean",
                "jack horner", "rayetta"]

water_pts = []
amenity_pts = []
mile_marker_pts = []
business_pts = []

for wpt in gpx.waypoints:
    raw_name = (wpt.name or "").strip()
    if not raw_name or raw_name.startswith("Directions") or \
       raw_name.startswith("Start Of") or raw_name.startswith("End of"):
        continue

    m = MILE_RE.match(raw_name)
    mile, label = (float(m.group(1)), m.group(2).strip()) if m else (None, raw_name)
    label_lower = label.lower()
    pt = Point(wpt.longitude, wpt.latitude)

    if label_lower.startswith("mile marker"):
        mile_marker_pts.append({"mile_marker": mile, "name": label, "geometry": pt})
        continue

    if not label:
        # pure mile-marker waypoints already handled above; skip empties
        continue

    record = {"mile_marker": mile, "name": raw_name, "label": label, "geometry": pt}

    if any(k in label_lower for k in water_kw):
        record["category"] = "water"
        water_pts.append(record)
    elif any(k in label_lower for k in shelter_kw):
        record["category"] = "campsite_shelter"
        amenity_pts.append(record)
    elif any(k in label_lower for k in bathroom_kw):
        record["category"] = "bathroom"
        amenity_pts.append(record)
    elif any(k in label_lower for k in repair_kw):
        record["category"] = "bike_repair"
        amenity_pts.append(record)
    elif any(k in label_lower for k in picnic_kw):
        record["category"] = "picnic"
        amenity_pts.append(record)
    elif any(k in label_lower for k in parking_kw):
        record["category"] = "trail_access"
        amenity_pts.append(record)
    elif any(k in label_lower for k in landmark_kw):
        record["category"] = "landmark"
        amenity_pts.append(record)
    elif any(k in label_lower for k in business_kw) or mile is None:
        record["category"] = "business_landmark"
        business_pts.append(record)
    else:
        record["category"] = "other"
        amenity_pts.append(record)

# Water layer
gdf_water = gpd.GeoDataFrame(water_pts, crs="EPSG:4326")
gdf_water.to_file(f"{OUT_DIR}/greenbrier_river_trail_water.geojson", driver="GeoJSON")
print(f"\nWater/well-pump waypoints: {len(gdf_water)}")
print(gdf_water[["mile_marker","name"]].sort_values("mile_marker").to_string(index=False))

# Amenities layer (shelters, bathrooms, bike repair, picnic, access, landmarks)
gdf_amenities = gpd.GeoDataFrame(amenity_pts, crs="EPSG:4326")
gdf_amenities.to_file(f"{OUT_DIR}/greenbrier_river_trail_amenities.geojson", driver="GeoJSON")
print(f"\nOther amenity waypoints: {len(gdf_amenities)}")
print(gdf_amenities["category"].value_counts().to_string())

# Business/landmark layer
gdf_business = gpd.GeoDataFrame(business_pts, crs="EPSG:4326")
gdf_business.to_file(f"{OUT_DIR}/greenbrier_river_trail_businesses.geojson", driver="GeoJSON")
print(f"\nBusiness/landmark waypoints: {len(gdf_business)}")
print(gdf_business["name"].tolist())
