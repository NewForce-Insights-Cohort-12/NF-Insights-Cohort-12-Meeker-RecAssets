# Recreation Capacity — ALT Corridor Town Explorer
### ALT-EXP — Allegheny Trail Corridor

**Scope:** Recreation assets, public lands, conservation easements, and private recreation facilities along the Allegheny Trail (ALT) corridor in West Virginia, organized by the 11 official corridor towns. This is one analyst's component of the larger ALT-EXP Allegheny Trail economic impact project.

**Primary deliverable:** `outputs/rec_capacity_town_explorer.html` — an interactive Leaflet.js dashboard. Select any corridor town from the dropdown to filter all map layers and populate data tables for public lands, amenities, private rec facilities, and conservation easements associated with that town.

**For group project integration:** see `data/exports/` — four clean CSV + GeoJSON pairs, one per layer, each with a `corridor_town` field.

---

## Corridor Towns

The 11 official corridor towns are defined in `data/focus_town_list.csv`:

| Town | County |
|------|--------|
| Albright | Preston |
| Terra Alta | Preston |
| Rowlesburg | Preston |
| Thomas | Tucker |
| Davis | Tucker |
| Jenningston | Webster |
| Green Bank | Pocahontas |
| Durbin | Pocahontas |
| Cass | Pocahontas |
| Marlinton | Pocahontas |
| White Sulphur Springs | Greenbrier |

Town boundaries are in `data/focus_towns.geojson` (10 polygons from Census TIGER; Jenningston has no Census boundary and uses a point proxy at -80.207, 38.866).

---

## Setup

```bash
pip install geopandas folium branca pandas jupyter pyproj shapely fiona
```

---

## Key Outputs

### Town Explorer Dashboard
`outputs/rec_capacity_town_explorer.html`

Self-contained Leaflet.js application (~4MB, all data embedded). Features:
- Town dropdown filters all four data layers simultaneously
- Summary bar: public land count, public land acres, amenity count, private rec count, easement count, easement acres
- 4-tab sidebar table: Public Lands / Amenities / Private Rec / Easements
- Static layers: ALT corridor boundary, trail route, Highland Scenic Highway (Rt. 150)
- Color-coded polygons and point markers by facility/holder type
- Legend

### Static Folium Map
`outputs/recreation_capacity_map.html`

Earlier deliverable built via the Jupyter notebook. Shows public land polygons, amenity points, Highland Scenic Highway, and trail route. Does not include the town-explorer filtering or private rec / easement layers.

---

## Data Exports (for group project integration)

`data/exports/` contains four CSV + GeoJSON pairs. All share a `corridor_town` field keyed to the 11 towns above.

| File pair | Features | Key fields |
|-----------|----------|------------|
| `public_lands.*` | 26 polygons | name, facility_type, agency, acres, notes, corridor_town |
| `amenities.*` | 14 points | name, amenity_type, associated_facility, notes, corridor_town |
| `private_rec.*` | 25 points | name, facility_type, address, county, notes, corridor_town |
| `easements.*` | 1,096 polygons | unit_name, holder, holder_type, manager, acres, duration, date_est, pub_access, gap_status, corridor_town |

---

## File Structure

```
recreation_capacity/
├── README.md
├── recreation_capacity_memo.md        # Earlier analytical memo (opportunity/pressure scorecard)
├── portfolio.html
│
├── data/
│   ├── focus_town_list.csv            # 11 official corridor towns with Census GEOIDs
│   ├── focus_towns.geojson            # Town boundary polygons (10 Census + 1 point proxy)
│   ├── town_scorecard.csv             # Earlier scorecard artifact (27 towns, pre-refocus)
│   ├── build_town_scorecard.py        # Builds the earlier scorecard
│   ├── build_map.py                   # Standalone script to regenerate recreation_capacity_map.html
│   │
│   ├── exports/                       # ← GROUP PROJECT INTEGRATION FILES
│   │   ├── public_lands.csv / .geojson
│   │   ├── amenities.csv / .geojson
│   │   ├── private_rec.csv / .geojson
│   │   └── easements.csv / .geojson
│   │
│   ├── recreation/
│   │   │
│   │   │  — Working / tagged files (all have nearest_town property) —
│   │   ├── public_lands_tagged.geojson          # 26 PAD-US polygons, with computed acres
│   │   ├── public_points_tagged.geojson         # Same 26 lands as point centroids
│   │   ├── amenities_tagged.geojson             # 14 amenity points (overlooks, campgrounds, etc.)
│   │   ├── private_rec_tagged.geojson           # 25 private facilities
│   │   ├── easements_tagged.geojson             # 1,096 PAD-US easement polygons
│   │   ├── highland_tagged.geojson              # Highland Scenic Highway (Rt. 150) LineString
│   │   │
│   │   │  — Source / pre-tag files —
│   │   ├── public_recreation_lands_poly.geojson # PAD-US polygons before town-join
│   │   ├── public_recreation_lands.geojson      # Earlier point-based public lands layer
│   │   ├── public_recreation_amenities.geojson  # Earlier amenities (pre-coordinate correction)
│   │   ├── conservation_easements.geojson       # PAD-US easements before town-join
│   │   ├── private_rec_facilities_expanded.geojson  # Private rec before town-join