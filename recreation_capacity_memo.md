# Recreation Assets, Public Lands & Community/Environmental Capacity
### ALT-EXP Working Memo — Allegheny Trail Corridor

**Question:** Where do recreation assets create opportunity, and where might tourism create pressure?

**Companion file:** `recreation_capacity_map.html` (interactive map) and `town_scorecard.csv` (underlying data, 27 corridor towns)

**v2 update:** Karst geology (WVGES 1968 karst-formations layer, via DOE EDX)
is now integrated into the pressure score. This changed the ranking
meaningfully — see "What changed" below if you saw the v1 version of this
memo.

---

## Town Scorecard

Every corridor town gets two independent scores, not one blended number — a
town can score high on opportunity *and* high on pressure at the same time
(that combination is in fact the most important pattern in this data, see
Cass below). Higher opportunity = more recreation assets + existing
commercial base to build on. Higher pressure = more fragmented/small water
infrastructure and less existing business capacity to absorb growth.

| Town | Opportunity | Pressure | On karst? | Recreation assets nearby | Outfitters | Existing businesses |
|---|---|---|---|---|---|---|
| Marlinton | **13** | 2 | No (0.05mi) | Watoga SP, Beartown SP, Droop Mtn Battlefield SP, GRT connection | 2 | 167 |
| Davis | 7 | 2 | No | Blackwater Falls SP, Canaan Valley Resort SP | 2 | 34 |
| Bruceton Mills | 7 | 2 | No | Cooper's Rock SF (near), Chestnut Ridge Park (near) | 0 | 20 |
| White Sulphur Springs | 5 | **4** | **Yes** | Greenbrier Resort (self-supplied) | 0 | 184 |
| Cass | 5 | **4** | No (0.45mi) | Cass Scenic Railroad SP, GRT terminus | 0 | 10 |
| Parsons | 5 | 2 | No | Monongahela NF (Otter Creek/Spruce Knob, near) | 0 | 101 |
| Durbin | 4 | 2 | No | Monongahela NF (Cheat Mountain) | 0 | 21 |
| Hillsboro | 3 | **6** | **Yes** | Droop Mountain Battlefield SP | 0 | 14 |
| Kingwood | 3 | 2 | No | none mapped | 0 | 199 |
| Terra Alta | 3 | 2 | No | none mapped | 0 | 75 |
| Albright | 3 | 2 | No | none mapped | 0 | 20 |
| Masontown | 3 | 0 | No | none mapped | 0 | 27 |
| Aurora | 2 | **6** | **Yes** | Cathedral SP | 0 | 17 |
| Hambleton | 2 | 3 | No | none mapped | 0 | 8 |
| Green Bank | 2 | 2 | No | Green Bank Observatory | 0 | 24 |
| Arbovale | 1 | 5 | No | none mapped | 0 | 8 |
| Bartow | 1 | 5 | No | none mapped | 0 | 5 |
| Cheat Lake* | 1 | 4 | **Yes** | none mapped | 0 | 243 |
| Brookhaven* | 1 | 4 | **Yes** | none mapped | 0 | 121 |
| Harman | 1 | 3 | **Yes** | none mapped | 0 | 9 |
| Rowlesburg | 1 | 2 | No | none mapped | 0 | 28 |
| Hendricks | 1 | 1 | No | none mapped | 0 | 5 |
| Thomas | 1 | 0 | No | none mapped | 0 | 60 |
| Huntersville | 0 | 5 | **Yes** | none mapped | 0 | 4 |
| Brandonville | 0 | 3 | No | none mapped | 0 | 2 |
| Frank | 0 | 3 | No | none mapped | 0 | 2 |
| St. George | 0 | 3 | No | none mapped | 0 | 2 |

*Cheat Lake and Brookhaven are Morgantown-metro spillover CDPs, not
trail-driven economies — their high business counts reflect that, not
trail tourism. They score low on opportunity here because the scoring logic
looks at recreation-asset proximity and outfitter presence, not raw business
count, which correctly screens them out without needing a manual exclusion.*

**What changed from v1 (pre-karst):** Hillsboro and Aurora moved from
pressure score 4 to **6**, now the corridor's two highest — both sit
directly on mapped karst geology. White Sulphur Springs, Cheat Lake,
Brookhaven, Harman, and Huntersville also picked up karst exposure and moved
up 2-3 points each. No town's opportunity score changed; karst only affects
the pressure axis. See structural finding 4 below for why this matters.

**Scoring logic** (see `data/build_town_scorecard.py` for exact formula):
opportunity = 2 points per recreation asset nearby + 2 points for having any
in-corridor outfitter + 0-3 points for existing business density tier.
pressure = 2 points if 3+ water systems serve fewer than 100 people, 2 points
for having no municipal community water system at all, 1 point if fewer than
10 existing businesses, **2 points if the town sits directly on mapped karst
geology** (new in v2). These are deliberately simple, relative rankings
within this corridor — not validated against an external benchmark — meant
to sort towns into rough categories for discussion, not to produce a
defensible index number for a funder.

---

## The four quadrants

**High opportunity, low pressure — ready to capture more.** Marlinton is the
standout: four mapped recreation assets, two outfitters, the highest existing
business base in the corridor (167), and a municipal water system running a
normal 2.27 people-per-connection ratio with capacity headroom. It also sits
just 0.05mi outside the nearest mapped karst polygon — close enough that this
is worth treating as a "watch" item rather than a clean pass (geologic
formation boundaries from a 1968 map aren't drawn with that kind of
precision). Davis and Bruceton Mills show the same low-pressure pattern at
smaller scale, both comfortably off karst (1.7mi and 5.7mi respectively).
These three towns already have the commercial and infrastructure base to be
the corridor's front-of-house.

**High opportunity, high pressure — the case that matters most.** Cass
remains the standout in this quadrant even before karst: a real draw (Cass
Scenic Railroad SP, GRT terminus) paired with only 10 businesses and no
municipal water system. **Hillsboro and Aurora are now the corridor's two
highest pressure scores (6 each)**, and the reason is karst: both sit
directly on mapped formations (Hillsboro on Greenbrier Group limestone,
Aurora likely on Helderberg Group near Cathedral State Park), have no
municipal water system, and have a real recreation asset pulling visitor
traffic (Droop Mountain Battlefield SP, Cathedral SP respectively). This is
the clearest version of the question this memo was scoped to answer:
visible recreation draw, genuine environmental exposure, thin capacity to
manage either. White Sulphur Springs also picked up karst exposure (it's a
classic Greenbrier Valley karst town) but its pressure score stays moderate
(4) because it does have a functioning municipal system — the risk there is
more about the geology under any *new, unconnected* development than about
the existing town center.

**Low opportunity, high pressure — vulnerable without the upside.** Arbovale
and Bartow remain the towns with the least to gain and comparatively high
exposure (no recreation asset, no outfitter, small fragmented water systems)
— though notably, neither sits on mapped karst, so their pressure is purely
a water-capacity/business-thinness story, not a geological one. Two new
entrants to this quadrant after the karst update: **Huntersville** (now
pressure 5, karst-exposed, zero recreation assets, only 4 businesses) and,
less severely, **Harman** (karst-exposed but has a functioning municipal
system, keeping its score moderate). Cheat Lake and Brookhaven also picked up
karst exposure, but as established, their high business counts are
Morgantown-metro-driven, not trail-driven, so the practical relevance of
their karst exposure to *this* project is lower than the others here.

**Low opportunity, low pressure — not the focus.** Kingwood, Terra Alta,
Albright, Rowlesburg, Hendricks, Thomas, and Masontown have functioning
municipal water systems, moderate business bases, and sit off mapped karst.
They're stable but largely outside this analysis's scope — the ALT isn't the
lever for these towns' economies one way or the other.

---

## Three structural findings

**1. Recreation assets cluster at two points: Marlinton and the Davis/Canaan
Valley area.** Of 27 corridor towns, only 10 have any mapped recreation asset
nearby, and Marlinton alone accounts for 4 of the corridor's most significant
assets plus the only direct connection to the Greenbrier River Trail. This
isn't a uniformly-distributed corridor — it has two real anchors and a long
tail of towns with no comparable draw.

**2. Public water capacity is fragmented almost everywhere, including in
high-opportunity towns.** Even Marlinton, the strongest performer, has 37
small/transient water systems (mostly individual motels, restaurants,
campgrounds on private wells) alongside its one solid municipal system.
That's not necessarily a problem today, but it means future
visitor-driven demand lands on dozens of separate small private systems
rather than one system with monitored capacity — worth tracking if visitor
volume grows, even in the towns best positioned to benefit.

**3. The clearest capacity gap is the absence of a municipal water system at
all, not the size of individual systems.** Cass, Hillsboro, Aurora, Bartow,
Arbovale, Green Bank, Hambleton, Cheat Lake, Brookhaven, Huntersville,
Brandonville, Frank, and St. George have no municipal CWS — water service in
these towns is some combination of private wells and small private systems.
For towns with a real recreation draw (Cass, Hillsboro, Aurora), that's the
single most concrete infrastructure question for further investigation: who
would serve increased demand, and is there room to.

**4. Karst geology and "no municipal water system" overlap more than chance
would predict.** Of the 7 towns sitting directly on mapped karst (White
Sulphur Springs, Hillsboro, Aurora, Cheat Lake, Brookhaven, Harman,
Huntersville), 5 also lack a municipal CWS. That's not a coincidence so much
as shared geography — the Greenbrier Valley karst belt runs through exactly
the part of the corridor (Greenbrier/Pocahontas counties) where towns tend
to be smaller and less likely to have invested in municipal water
infrastructure historically. The practical implication: in these towns, any
tourism-driven development that isn't tied into a monitored municipal system
is going onto a private well over karst bedrock, where the WVGES's own
description of the terrain — sinkholes, sinking streams, subterranean
drainage — means contamination travels fast and is hard to trace back to its
source. This is the most concrete environmental-pressure mechanism this
analysis has identified, and it's specific to a fairly small number of named
towns, not a corridor-wide concern.

---

## What's not yet in this analysis

- **Housing/short-term-rental capacity** — no data source identified yet.
  Relevant to pressure (does increased tourism compete with resident housing
  stock) but out of scope for this pass.
- **Emergency services (EMS/fire response coverage)** — mentioned as a
  capacity dimension in early project scoping, not yet pursued.
- **Recreation asset list is a starter set** (14 lands, 14 amenities) per the
  main project README — Cooper's Rock, Chestnut Ridge Park, and the
  USFS Spruce Knob/Otter Creek cluster near Parsons are known-but-unmapped
  assets that would change Bruceton Mills' and Parsons' opportunity scores
  if added.
- **Karst layer is a 1968-derived generalized map, not parcel-level data.**
  The on_karst flag is a polygon-intersection test against town boundaries,
  not a finding about any specific well or septic system. Marlinton's
  0.05mi near-miss is a reminder that boundary precision at this scale
  shouldn't be read as exact — a town just outside a mapped karst polygon on
  a 1968 map could easily have karst features in reality. Treat on_karst as
  "flagged for further look," not as a definitive yes/no.

## Suggested next steps

1. ~~Get the WVGES/EDX karst layer and overlay it against the
   pressure-score towns~~ — **done in v2**. Confirmed the hypothesized
   Greenbrier/Pocahontas county overlap; Hillsboro and Aurora are now the
   corridor's highest-pressure towns as a result.
2. Spot-check the "no municipal CWS" towns (especially Cass, Hillsboro,
   Aurora) — confirm directly whether that's accurate or a gap in how SDWIS
   records small/unincorporated places, since this is the single largest
   swing factor in the pressure score, and now compounds with karst exposure
   for two of these three towns.
3. If time allows, add the Cooper's Rock/Chestnut Ridge/Spruce Knob/Otter
   Creek recreation assets already identified in the main project's "Known
   issues" list — this would directly raise Bruceton Mills' and Parsons'
   opportunity scores and may surface a second high-opportunity/high-pressure
   case near Parsons worth flagging alongside Cass.
4. Consider a parcel- or well-level data source (WV DHHR SWAP reports,
   mentioned in the main project's environmental data discussion) for the
   karst-exposed, no-municipal-CWS towns specifically — that's a small
   enough list (White Sulphur Springs, Hillsboro, Aurora, Harman,
   Huntersville) to make a deeper per-town look feasible.
