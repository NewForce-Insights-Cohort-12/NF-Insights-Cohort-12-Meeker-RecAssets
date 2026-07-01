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

## Visitor Data

Annual visitor counts were researched for all 51 facilities (26 public lands, 25 private rec) and added as five new columns to both export CSVs and GeoJSON files: `annual_visitors`, `visitor_year`, `visitor_trend`, `visitor_source`, `visitor_data_notes`. The dashboard and town explorer sidebar tables now display this data where available.

### Facilities with confirmed visitor data (7 of 51)

| Facility | Annual Visitors | Year | Source |
|----------|----------------|------|--------|
| New River Gorge NP & Preserve | 1,811,937 (record) | 2024 | NPS IRMA Stats (irma.nps.gov) |
| Snowshoe Mountain Resort | ~480,000 skier visits | 2022–23 est. | skimag.com; snowshoemtn.com |
| Coopers Rock State Forest | ~300,000 | 2023 est. | coopersrock.org; visitmountaineercountry.com |
| Dolly Sods Wilderness | ~60,000 (range 45K–76K) | 2022–23 | wvgazettemail.com; wvhighlands.org |
| Green Bank Observatory | ~50,000 | 2023 est. | gogreenbankobservatory.org (official fact sheets) |
| Spruce Knob-Seneca Rocks NRA | ~35,000 (Seneca Rocks area) | 2023 est. | USFS NVUM; wvtourism.com |
| Canaan Valley NWR | ~10,000 (visitor center only) | 2023 est. | USFWS (fws.gov/refuge/canaan-valley) |

**NRG context:** New River Gorge NP grew 1,595,923 (2022) → 1,709,623 (2023) → 1,811,937 (2024), ~6%/yr. Gauley River NRA (adjacent, not in this dataset) saw 187,223 visitors in 2023.

**Monongahela NF context:** The Mon NF as a whole receives ~3 million visits/year (USFS NVUM FY2019), but individual wilderness unit counts are not published. Dolly Sods trailhead registers are the one exception with tracked counts.

### Why 44 facilities have no visitor data

- **WV DNR state parks/forests** (~14 facilities): WV DNR does not publish facility-level annual visitor counts. The agency reports only a system-wide aggregate (~7 million/year across all state parks). Counts for individual parks such as Blackwater Falls, Watoga, and Cass Scenic Railroad are maintained internally but not released publicly.
- **Private facilities** (~24 facilities): Private companies (outfitters, resorts, campgrounds, summer camps, golf courses) are not required to report visitor figures and rarely publish them.
- **USFS wilderness areas** (Otter Creek, Laurel Fork N/S, Cranberry): No formal visitor counting infrastructure. Dolly Sods is the exception because WV Highlands Conservancy has run a trailhead register program there.

### Recommended next steps to fill gaps

1. **WV DNR public records request** — submit a FOIA/public records request to WV Division of Natural Resources for annual park-level visitation counts. Contact: wvdnr.gov.
2. **New River Gorge CVB** — the Convention & Visitors Bureau (newrivergorgecvb.com) may have aggregated commercial outfitter permit data for the New/Gauley rafting industry.
3. **USFS Monongahela NF NVUM** — the next National Visitor Use Monitoring survey cycle (every 5 ye