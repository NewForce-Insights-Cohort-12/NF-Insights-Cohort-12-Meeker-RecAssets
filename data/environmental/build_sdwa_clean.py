"""
Parses the transcribed Approach A (city-name match) output into a structured
CSV, then applies cleaning steps:
  1. Collapse the ~50 duplicate "ALYESKA INC" entries (Bruceton Mills /
     Alpine Lake Resort per-lot wells) into a single summary row
  2. Drop inactive systems (PWS_ACTIVITY_CODE == 'I')
  3. Drop the two Mason Co PSD entries (data error - Mason County is ~150mi away)

OUTPUT:
  sdwa_corridor_systems_clean.csv - final cleaned corridor water systems dataset
"""

import re
import pandas as pd

RAW_PATH = "/home/claude/alt_project/data/environmental/raw_approach_a.txt"
OUT_PATH = "/home/claude/alt_project/data/environmental/sdwa_corridor_systems_clean.csv"

CORRIDOR_TOWNS = [
    "BRUCETON MILLS", "WHITE SULPHUR SPRINGS", "TERRA ALTA", "GREEN BANK",
    "ST. GEORGE", "ST GEORGE", "ARBOVALE", "ALBRIGHT", "AURORA", "BARTOW",
    "BOWDEN", "CASS", "DAVIS", "DURBIN", "FRANK", "HARMAN", "HENDRICKS",
    "HILLSBORO", "KINGWOOD", "MARLINTON", "MASONTOWN", "PARSONS",
    "ROWLESBURG", "THOMAS",
]
# longest-first so multi-word towns match before single-word substrings
CORRIDOR_TOWNS_SORTED = sorted(CORRIDOR_TOWNS, key=len, reverse=True)

PWS_TYPES = ["NTNCWS", "TNCWS", "CWS"]

rows = []
with open(RAW_PATH) as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue

        # PWSID is the first whitespace-delimited token
        m = re.match(r"^(\S+)\s+(.*)$", line)
        pwsid, rest = m.group(1), m.group(2)

        # find city name (try longest multi-word matches first)
        city = None
        for town in CORRIDOR_TOWNS_SORTED:
            # city name should be right before the PWS_TYPE_CODE
            pattern = r"\s+(" + re.escape(town) + r")\s+(NTNCWS|TNCWS|CWS)\s+"
            mm = re.search(pattern, rest)
            if mm:
                city = mm.group(1)
                # everything before city = PWS_NAME
                pws_name = rest[:mm.start()].strip()
                tail = rest[mm.end():]
                pws_type = mm.group(2)
                break
        if city is None:
            print("WARNING: could not parse line:", line)
            continue

        # tail now: OWNER_TYPE_CODE  POP  CONN  ACTIVITY
        tail_parts = tail.split()
        owner_type, pop, conn, activity = tail_parts[0], tail_parts[1], tail_parts[2], tail_parts[3]

        rows.append({
            "PWSID": pwsid,
            "PWS_NAME": pws_name,
            "CITY_NAME": city,
            "PWS_TYPE_CODE": pws_type,
            "OWNER_TYPE_CODE": owner_type,
            "POPULATION_SERVED_COUNT": int(pop),
            "SERVICE_CONNECTIONS_COUNT": int(conn),
            "PWS_ACTIVITY_CODE": activity,
        })

df = pd.DataFrame(rows)
print(f"Parsed {len(df)} rows")

# --- Cleaning step 1: collapse ALYESKA INC duplicates ---
alyeska_mask = df["PWS_NAME"].str.contains("ALYESKA", case=False, na=False)
alyeska_rows = df[alyeska_mask]
n_alyeska = len(alyeska_rows)
n_active = (alyeska_rows["PWS_ACTIVITY_CODE"] == "A").sum()
total_pop = alyeska_rows.loc[alyeska_rows["PWS_ACTIVITY_CODE"] == "A", "POPULATION_SERVED_COUNT"].sum()
total_conn = alyeska_rows.loc[alyeska_rows["PWS_ACTIVITY_CODE"] == "A", "SERVICE_CONNECTIONS_COUNT"].sum()

df = df[~alyeska_mask].copy()

summary_row = {
    "PWSID": "MULTIPLE",
    "PWS_NAME": f"ALYESKA INC (Alpine Lake Resort) - {n_active} active per-lot/unit wells, "
                f"{n_alyeska - n_active} inactive [collapsed from individual PWSIDs]",
    "CITY_NAME": "BRUCETON MILLS",
    "PWS_TYPE_CODE": "TNCWS",
    "OWNER_TYPE_CODE": "P",
    "POPULATION_SERVED_COUNT": int(total_pop),
    "SERVICE_CONNECTIONS_COUNT": int(total_conn),
    "PWS_ACTIVITY_CODE": "A",
}
df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
print(f"Collapsed {n_alyeska} ALYESKA entries ({n_active} active) into 1 summary row "
      f"(total active pop served: {total_pop}, connections: {total_conn})")

# --- Cleaning step 2: drop inactive systems ---
n_before = len(df)
df = df[df["PWS_ACTIVITY_CODE"] != "I"].copy()
print(f"Dropped {n_before - len(df)} inactive systems")

# --- Cleaning step 3: drop Mason Co PSD entries (data error, ~150mi from corridor) ---
mason_mask = df["PWS_NAME"].str.contains("MASON CO PSD", case=False, na=False)
print(f"Dropping {mason_mask.sum()} Mason Co PSD entries (data error - Mason County "
      f"is on the Ohio River, not in the corridor)")
df = df[~mason_mask].copy()

df = df.sort_values(["CITY_NAME", "PWS_TYPE_CODE", "PWS_NAME"]).reset_index(drop=True)
df.to_csv(OUT_PATH, index=False)

print(f"\nFinal cleaned dataset: {len(df)} systems -> {OUT_PATH}")
print("\nBy city:")
print(df["CITY_NAME"].value_counts().to_string())
print("\nBy type:")
print(df["PWS_TYPE_CODE"].value_counts().to_string())
