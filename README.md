# Recreation Assets, Public Lands & Community/Environmental Capacity
### ALT-EXP — Allegheny Trail Corridor

**Scope:** Where do recreation assets create opportunity, and where might
tourism create pressure? This is one analyst's piece of the larger ALT-EXP
Allegheny Trail economic impact project — a focused recombination of the
broader project's data around the opportunity-vs-pressure question, not a
comprehensive corridor inventory.

**Start here:** `recreation_capacity_memo.md` (scorecard + analysis) and
`outputs/recreation_capacity_map.html` (interactive map).

## Setup

```bash
pip install geopandas folium branca pandas jupyter
```

## Usage

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/recreation_capacity_map.ipynb
```

Map saves to `outputs/recreation_capacity_map.html`.

To rebuild the town scorecard (e.g. after adding recreation assets or
re-pulling SDWA data):

```bash
python3 data/build_town_scorecard.py
```

## Structure

```
recreation_capacity/
├── recreation_capacity_memo.md       # Main deliverable: scorecard + analysis
├── data/
│   ├── town_scorecard.csv            # Core analytical artifact, 27 towns
│   ├── build_town_scorecard.py       # Builds the scorecard from source data
│   ├── recreation/
│   │   ├── public_recreation_lands.geojson
│   │   ├── public_recreation_amenities.geojson
│   │   ├── greenbrier_river_trail_centerline.geojson
│   │   ├── greenbrier_river_trail_water.geojson
│   │   └── greenbrier_river_trail_amenities.geojson
│   ├── environmental/
│   │   ├── sdwa_corridor_systems_clean.csv   # 188 EPA SDWIS public water systems
│   │   └── karst/
│   │       ├── karst_corridor_clip.geojson           # 64 polygons, clipped to ~10mi of corridor
│   │       └── geologyKarstFormations_WVGES_1968_ll83.* # Full statewide shapefile (source)
│   ├── business/
│   │   ├── trail_corridor_business_totals.csv
│   │   └── outfitter_businesses.geojson
│   ├── boundaries/
│   │   ├── incorporated_place.geojson        # For town geometry joins
│   │   └── census_designated_place.geojson
│   └── trail/
│       ├── allegheny_trail_master_route.geojson
│       ├── alt_corridor_5mi_v2.geojson
│       └── alt_waypoints.geojson
├── notebooks/
│   └── recreation_capacity_map.ipynb
└── outputs/
    └── recreation_capacity_map.html
```

Most files here are copied from the main ALT-EXP combined-map project
(`jimmyboggs-wv/NF-Insights-Cohort-12-Data-Repo`) — see that project's
README for full data provenance, sourcing details, and known data-quality
caveats on each input. This README only documents what's specific to the
opportunity/pressure scorecard built on top of that shared data.

## The scorecard

`town_scorecard.csv` is the core analytical artifact. Each town gets two
independent 0-13-ish scores (not normalized to a fixed scale — relative
ranking within this corridor only):

- **opportunity_score** = 2 × (recreation assets nearby) + 2 × (has any
  in-corridor outfitter) + 0-3 (existing business density tier)
- **pressure_score** = 2 × (3+ water systems serving <100 people) + 2 × (no
  municipal community water system) + 1 × (fewer than 10 existing
  businesses) + 2 × (town sits directly on mapped karst geology)

**Karst data source**: WVGES's 1968-derived generalized karst-potential map
(`geologyKarstFormations_WVGES_1968_ll83.shp`), sourced via DOE's EDX
platform (`edx.netl.doe.gov/dataset/west-virginia-geology-karst-regions`),
originally extracted by the WV Bureau of Public Health from the statewide
1968 geologic map's limestone/dolomite formations. 250 polygons statewide,
64 within ~10mi of the corridor (`karst_corridor_clip.geojson`). Karst status
per town is a polygon-intersection test against town boundaries (see
`town_karst_status()` in `build_town_scorecard.py`) — not a parcel- or
well-level finding.

See `recreation_capacity_memo.md` for the full breakdown and discussion of
what these scores mean town-by-town, and `build_town_scorecard.py` for the
exact join/aggregation logic.

**Caveat on the recreation-asset proximity mapping**: which recreation
assets are "near" which town (`RECREATION_NEAR_TOWN` dict in
`build_town_scorecard.py`) is hand-coded from earlier project analysis, not
a computed distance join. A few assets are flagged `(near, unmapped)`
because they're known to exist near a town (e.g. Cooper's Rock State Forest
near Bruceton Mills) but aren't yet in `public_recreation_lands.geojson` —
adding them would change that town's score.

## Known gaps (see memo for full discussion)

- No housing/short-term-rental capacity data.
- No emergency services (EMS/fire) coverage data.
- Recreation asset inventory is a starter set (14 lands, 14 amenities) -
  several known assets (Cooper's Rock, Chestnut Ridge Park, USFS
  Spruce Knob/Otter Creek cluster) aren't mapped yet.
- Karst layer (`data/environmental/karst/`) is a 1968-derived generalized
  map, not parcel-level - treat `on_karst` in the scorecard as "flagged for
  further look," not a definitive yes/no. See memo for the Marlinton
  0.05mi near-miss case.
