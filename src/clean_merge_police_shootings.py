import csv, os, zipfile, math, json
from datetime import datetime
from collections import defaultdict, Counter

BASE_DIR = "/mnt/data"
UNZIP_DIR = os.path.join(BASE_DIR, "police_shootings_unzipped")
REPO_DIR = os.path.join(UNZIP_DIR, "data-police-shootings-master")
INCIDENTS_PATH = os.path.join(REPO_DIR, "v2", "fatal-police-shootings-data.csv")
AGENCIES_PATH = os.path.join(REPO_DIR, "v2", "fatal-police-shootings-agencies.csv")
POP_2019_PATH = os.path.join(BASE_DIR, "nst-est2019-alldata.csv")
POP_2025_PATH = os.path.join(BASE_DIR, "NST-EST2025-ALLDATA.csv")
OUT_DIR = os.path.join(BASE_DIR, "police_shootings_cleaned_percapita")
os.makedirs(OUT_DIR, exist_ok=True)

STATE_ABBR_BY_FIPS = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
    "72": "PR",
}
FIPS_BY_STATE_ABBR = {v: k for k, v in STATE_ABBR_BY_FIPS.items()}
RACE_LABELS = {
    "W": "White",
    "B": "Black",
    "A": "Asian heritage",
    "N": "Native American",
    "H": "Hispanic",
    "O": "Other",
}

# Load Census state names from population files.
state_name_by_fips = {}


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


for p in [POP_2019_PATH, POP_2025_PATH]:
    for r in read_csv(p):
        if r.get("SUMLEV") == "040" and r.get("STATE") in STATE_ABBR_BY_FIPS:
            state_name_by_fips[r["STATE"]] = r["NAME"]
state_name_by_fips["11"] = "District of Columbia"
state_name_by_fips["72"] = "Puerto Rico"
STATE_NAME_BY_ABBR = {
    STATE_ABBR_BY_FIPS[f]: name for f, name in state_name_by_fips.items()
}

# Population long table, 2015-2025. For 2015-2019 use Vintage 2019; 2020-2025 use Vintage 2025.
pop_rows = []
for r in read_csv(POP_2019_PATH):
    if r.get("SUMLEV") == "040" and r.get("STATE") in STATE_ABBR_BY_FIPS:
        fips = r["STATE"]
        abbr = STATE_ABBR_BY_FIPS[fips]
        for year in range(2015, 2020):
            val = r.get(f"POPESTIMATE{year}", "")
            pop_rows.append(
                {
                    "year": year,
                    "state_abbr": abbr,
                    "state_fips": fips,
                    "state_name": state_name_by_fips.get(fips, r.get("NAME", "")),
                    "population": int(val) if val else "",
                    "population_source_vintage": "Census PEP Vintage 2019",
                    "population_source_url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv",
                }
            )
for r in read_csv(POP_2025_PATH):
    if r.get("SUMLEV") == "040" and r.get("STATE") in STATE_ABBR_BY_FIPS:
        fips = r["STATE"]
        abbr = STATE_ABBR_BY_FIPS[fips]
        for year in range(2020, 2026):
            val = r.get(f"POPESTIMATE{year}", "")
            pop_rows.append(
                {
                    "year": year,
                    "state_abbr": abbr,
                    "state_fips": fips,
                    "state_name": state_name_by_fips.get(fips, r.get("NAME", "")),
                    "population": int(val) if val else "",
                    "population_source_vintage": "Census PEP Vintage 2025",
                    "population_source_url": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv",
                }
            )
# Add national population rows too.
for r in read_csv(POP_2019_PATH):
    if r.get("SUMLEV") == "010":
        for year in range(2015, 2020):
            pop_rows.append(
                {
                    "year": year,
                    "state_abbr": "US",
                    "state_fips": "00",
                    "state_name": "United States",
                    "population": int(r[f"POPESTIMATE{year}"]),
                    "population_source_vintage": "Census PEP Vintage 2019",
                    "population_source_url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv",
                }
            )
for r in read_csv(POP_2025_PATH):
    if r.get("SUMLEV") == "010":
        for year in range(2020, 2026):
            pop_rows.append(
                {
                    "year": year,
                    "state_abbr": "US",
                    "state_fips": "00",
                    "state_name": "United States",
                    "population": int(r[f"POPESTIMATE{year}"]),
                    "population_source_vintage": "Census PEP Vintage 2025",
                    "population_source_url": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv",
                }
            )

pop_by_state_year = {
    (r["state_abbr"], int(r["year"])): int(r["population"])
    for r in pop_rows
    if r["population"] != ""
}

# Clean agencies.
agencies_raw = read_csv(AGENCIES_PATH)
clean_agencies = []
agency_by_id = {}
for r in agencies_raw:
    aid = r.get("id", "").strip()
    state = r.get("state", "").strip().upper()
    fips = FIPS_BY_STATE_ABBR.get(state, "")
    ori_codes = [x.strip() for x in r.get("oricodes", "").split(";") if x.strip()]
    out = {
        "agency_id": int(aid) if aid.isdigit() else aid,
        "agency_name": r.get("name", "").strip(),
        "agency_type": r.get("type", "").strip() or "missing",
        "agency_state_abbr": state,
        "agency_state_fips": fips,
        "agency_state_name": STATE_NAME_BY_ABBR.get(state, ""),
        "ori_codes": ";".join(ori_codes),
        "ori_code_count": len(ori_codes),
        "agency_total_shootings_original": int(r["total_shootings"])
        if r.get("total_shootings", "").isdigit()
        else "",
    }
    clean_agencies.append(out)
    agency_by_id[str(out["agency_id"])] = out

# Helpers.
def to_float(x):
    x = (x or "").strip()
    if x == "":
        return ""
    try:
        return float(x)
    except ValueError:
        return ""


def to_int(x):
    x = (x or "").strip()
    if x == "":
        return ""
    try:
        return int(float(x))
    except ValueError:
        return ""


def clean_bool(x):
    x = (x or "").strip().lower()
    if x == "true":
        return True
    if x == "false":
        return False
    return ""


def age_group(age):
    if age == "":
        return "Unknown"
    if age < 18:
        return "0-17"
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    if age < 65:
        return "55-64"
    return "65+"


def label_race(code):
    codes = [c.strip() for c in (code or "").split(";") if c.strip()]
    if not codes:
        return "Unknown"
    labels = [RACE_LABELS.get(c, c) for c in codes]
    if len(labels) == 1:
        return labels[0]
    return "; ".join(labels)


def clean_flee(x):
    x = (x or "").strip()
    if x == "":
        return "missing"
    if x == "not":
        return "not_fleeing"
    return x


def clean_missing(x):
    x = (x or "").strip()
    return x if x else "missing"


# Clean incidents and build incident-agency bridge.
incidents_raw = read_csv(INCIDENTS_PATH)
clean_incidents = []
bridge_rows = []
for r in incidents_raw:
    dt = datetime.strptime(r["date"], "%Y-%m-%d")
    year, month = dt.year, dt.month
    state = (r.get("state") or "").strip().upper()
    fips = FIPS_BY_STATE_ABBR.get(state, "")
    age = to_int(r.get("age", ""))
    lat = to_float(r.get("latitude", ""))
    lon = to_float(r.get("longitude", ""))
    race_codes = [c.strip() for c in (r.get("race") or "").split(";") if c.strip()]
    armed_codes = [
        c.strip() for c in (r.get("armed_with") or "").split(";") if c.strip()
    ]
    agency_ids = [
        a.strip() for a in (r.get("agency_ids") or "").split(";") if a.strip()
    ]
    out = {
        "incident_id": int(r["id"]) if r.get("id", "").isdigit() else r.get("id", ""),
        "incident_date": r["date"],
        "year": year,
        "month": month,
        "quarter": f"Q{((month-1)//3)+1}",
        "city": (r.get("city") or "").strip(),
        "county": (r.get("county") or "").strip(),
        "state_abbr": state,
        "state_fips": fips,
        "state_name": STATE_NAME_BY_ABBR.get(state, ""),
        "latitude": lat,
        "longitude": lon,
        "has_coordinates": bool(lat != "" and lon != ""),
        "location_precision": clean_missing(r.get("location_precision")),
        "victim_name": (r.get("name") or "").strip(),
        "age": age,
        "age_group": age_group(age),
        "gender": clean_missing(r.get("gender")),
        "race_codes": ";".join(race_codes),
        "race_label": label_race(r.get("race")),
        "race_known": bool(race_codes),
        "race_is_multi_value": len(race_codes) > 1,
        "race_source": clean_missing(r.get("race_source")),
        "was_mental_illness_related": clean_bool(r.get("was_mental_illness_related")),
        "body_camera": clean_bool(r.get("body_camera")),
        "threat_type": clean_missing(r.get("threat_type")),
        "flee_status": clean_flee(r.get("flee_status")),
        "armed_with": ";".join(armed_codes) if armed_codes else "missing",
        "armed_category_count": len(armed_codes),
        "is_unarmed": ("unarmed" in armed_codes),
        "armed_with_gun": ("gun" in armed_codes),
        "armed_with_vehicle": ("vehicle" in armed_codes),
        "armed_unknown_or_undetermined": any(
            c in ("unknown", "undetermined") for c in armed_codes
        ),
        "agency_ids": ";".join(agency_ids),
        "agency_count": len(agency_ids),
        "source_dataset": "Washington Post Fatal Force v2 uploaded ZIP",
    }
    clean_incidents.append(out)
    for aid in agency_ids:
        ag = agency_by_id.get(aid)
        bridge_rows.append(
            {
                "incident_id": out["incident_id"],
                "incident_date": out["incident_date"],
                "year": year,
                "state_abbr": state,
                "agency_id": int(aid) if aid.isdigit() else aid,
                "agency_name": ag["agency_name"] if ag else "",
                "agency_type": ag["agency_type"] if ag else "",
                "agency_state_abbr": ag["agency_state_abbr"] if ag else "",
                "agency_state_name": ag["agency_state_name"] if ag else "",
                "multi_agency_incident": len(agency_ids) > 1,
            }
        )

# State-year summary.
state_year = defaultdict(lambda: Counter())
for r in clean_incidents:
    key = (r["year"], r["state_abbr"])
    state_year[key]["fatal_shootings"] += 1
    if r["is_unarmed"]:
        state_year[key]["unarmed_count"] += 1
    if r["armed_with_gun"]:
        state_year[key]["armed_with_gun_count"] += 1
    if r["was_mental_illness_related"] is True:
        state_year[key]["mental_illness_related_count"] += 1
    if r["body_camera"] is True:
        state_year[key]["body_camera_count"] += 1
    if r["flee_status"] != "not_fleeing":
        state_year[key]["fleeing_or_missing_count"] += 1
    if r["race_known"]:
        state_year[key]["race_known_count"] += 1
    if not r["race_known"]:
        state_year[key]["race_missing_count"] += 1
state_year_rows = []
for (year, state), c in sorted(state_year.items()):
    pop = pop_by_state_year.get((state, year), "")
    denom = pop if pop else None
    fips = FIPS_BY_STATE_ABBR.get(state, "")
    shootings = c["fatal_shootings"]
    row = {
        "year": year,
        "state_abbr": state,
        "state_fips": fips,
        "state_name": STATE_NAME_BY_ABBR.get(state, ""),
        "fatal_shootings": shootings,
        "population": pop,
        "fatal_shootings_per_100k": round(shootings / denom * 100000, 4)
        if denom
        else "",
        "fatal_shootings_per_1m": round(shootings / denom * 1000000, 4)
        if denom
        else "",
        "unarmed_count": c["unarmed_count"],
        "unarmed_per_1m": round(c["unarmed_count"] / denom * 1000000, 4)
        if denom
        else "",
        "armed_with_gun_count": c["armed_with_gun_count"],
        "armed_with_gun_per_1m": round(c["armed_with_gun_count"] / denom * 1000000, 4)
        if denom
        else "",
        "mental_illness_related_count": c["mental_illness_related_count"],
        "mental_illness_related_per_1m": round(
            c["mental_illness_related_count"] / denom * 1000000, 4
        )
        if denom
        else "",
        "body_camera_count": c["body_camera_count"],
        "body_camera_per_1m": round(c["body_camera_count"] / denom * 1000000, 4)
        if denom
        else "",
        "race_known_count": c["race_known_count"],
        "race_missing_count": c["race_missing_count"],
        "population_source_vintage": next(
            (
                p["population_source_vintage"]
                for p in pop_rows
                if p["state_abbr"] == state and p["year"] == year
            ),
            "",
        ),
        "population_source_url": next(
            (
                p["population_source_url"]
                for p in pop_rows
                if p["state_abbr"] == state and p["year"] == year
            ),
            "",
        ),
    }
    state_year_rows.append(row)

# National summary.
national = defaultdict(lambda: Counter())
for r in clean_incidents:
    y = r["year"]
    national[y]["fatal_shootings"] += 1
    if r["is_unarmed"]:
        national[y]["unarmed_count"] += 1
    if r["armed_with_gun"]:
        national[y]["armed_with_gun_count"] += 1
    if r["was_mental_illness_related"] is True:
        national[y]["mental_illness_related_count"] += 1
    if r["body_camera"] is True:
        national[y]["body_camera_count"] += 1
    if r["race_known"]:
        national[y]["race_known_count"] += 1
    else:
        national[y]["race_missing_count"] += 1
national_rows = []
for year, c in sorted(national.items()):
    pop = pop_by_state_year.get(("US", year), "")
    denom = pop if pop else None
    shootings = c["fatal_shootings"]
    national_rows.append(
        {
            "year": year,
            "fatal_shootings": shootings,
            "population": pop,
            "fatal_shootings_per_100k": round(shootings / denom * 100000, 4)
            if denom
            else "",
            "fatal_shootings_per_1m": round(shootings / denom * 1000000, 4)
            if denom
            else "",
            "unarmed_count": c["unarmed_count"],
            "unarmed_per_1m": round(c["unarmed_count"] / denom * 1000000, 4)
            if denom
            else "",
            "armed_with_gun_count": c["armed_with_gun_count"],
            "armed_with_gun_per_1m": round(
                c["armed_with_gun_count"] / denom * 1000000, 4
            )
            if denom
            else "",
            "mental_illness_related_count": c["mental_illness_related_count"],
            "mental_illness_related_per_1m": round(
                c["mental_illness_related_count"] / denom * 1000000, 4
            )
            if denom
            else "",
            "body_camera_count": c["body_camera_count"],
            "body_camera_per_1m": round(c["body_camera_count"] / denom * 1000000, 4)
            if denom
            else "",
            "race_known_count": c["race_known_count"],
            "race_missing_count": c["race_missing_count"],
            "population_source_vintage": "Census PEP Vintage 2019"
            if year <= 2019
            else "Census PEP Vintage 2025",
        }
    )

# State overall summary.
state_overall = defaultdict(lambda: Counter())
pop_avg = defaultdict(list)
for r in pop_rows:
    if r["state_abbr"] not in ("US", "PR") and 2015 <= int(r["year"]) <= 2024:
        pop_avg[r["state_abbr"]].append(int(r["population"]))
for r in clean_incidents:
    state = r["state_abbr"]
    state_overall[state]["fatal_shootings"] += 1
    if r["is_unarmed"]:
        state_overall[state]["unarmed_count"] += 1
    if r["was_mental_illness_related"] is True:
        state_overall[state]["mental_illness_related_count"] += 1
state_overall_rows = []
for state, c in sorted(state_overall.items()):
    avg_pop = round(sum(pop_avg[state]) / len(pop_avg[state])) if pop_avg[state] else ""
    years = 10
    annualized_rate = (
        c["fatal_shootings"] / avg_pop / years * 1_000_000 if avg_pop else ""
    )
    state_overall_rows.append(
        {
            "state_abbr": state,
            "state_fips": FIPS_BY_STATE_ABBR.get(state, ""),
            "state_name": STATE_NAME_BY_ABBR.get(state, ""),
            "fatal_shootings_2015_2024": c["fatal_shootings"],
            "avg_population_2015_2024": avg_pop,
            "annualized_fatal_shootings_per_1m": round(annualized_rate, 4)
            if annualized_rate != ""
            else "",
            "unarmed_count_2015_2024": c["unarmed_count"],
            "mental_illness_related_count_2015_2024": c["mental_illness_related_count"],
        }
    )
state_overall_rows.sort(
    key=lambda x: x["annualized_fatal_shootings_per_1m"]
    if x["annualized_fatal_shootings_per_1m"] != ""
    else -1,
    reverse=True,
)
rank = 1
for r in state_overall_rows:
    r["rank_by_annualized_rate_per_1m"] = rank
    rank += 1

# Race-year summary numerator only + per total population (not race-specific denominator).
race_year = defaultdict(lambda: Counter())
for r in clean_incidents:
    labels = [RACE_LABELS.get(c, c) for c in r["race_codes"].split(";") if c]
    if not labels:
        labels = ["Unknown"]
    for label in labels:
        race_year[(r["year"], label)]["count_any_mention"] += 1
    # single/multivalue group as row too
race_year_rows = []
for (year, label), c in sorted(race_year.items()):
    pop = pop_by_state_year.get(("US", year), "")
    race_year_rows.append(
        {
            "year": year,
            "race_or_ethnicity_label": label,
            "fatal_shootings_count_any_mention": c["count_any_mention"],
            "us_total_population": pop,
            "rate_per_1m_total_us_population_NOT_GROUP_SPECIFIC": round(
                c["count_any_mention"] / pop * 1_000_000, 4
            )
            if pop
            else "",
            "denominator_warning": "This uses total U.S. population, not race/ethnicity-specific population. Do not treat as within-group risk rate.",
        }
    )

# Data dictionary.
data_dictionary = [
    {
        "table": "clean_incidents",
        "field": "incident_id",
        "definition": "Unique Fatal Force incident/victim ID from source v2 file.",
    },
    {
        "table": "clean_incidents",
        "field": "year/month/quarter",
        "definition": "Derived from incident_date for time-series analysis.",
    },
    {
        "table": "clean_incidents",
        "field": "state_fips/state_name",
        "definition": "Added using Census/USPS state crosswalk to support joins with population denominators.",
    },
    {
        "table": "clean_incidents",
        "field": "race_label",
        "definition": "Human-readable expansion of source race/ethnicity codes; multi-value source records are semicolon-expanded in the label.",
    },
    {
        "table": "clean_incidents",
        "field": "is_unarmed",
        "definition": "True when armed_with includes unarmed.",
    },
    {
        "table": "clean_incidents",
        "field": "armed_with_gun",
        "definition": "True when armed_with includes gun.",
    },
    {
        "table": "clean_incidents",
        "field": "agency_count",
        "definition": "Count of semicolon-delimited agencies in agency_ids.",
    },
    {
        "table": "incident_agency_bridge",
        "field": "agency_id",
        "definition": "One row per incident-agency pair. Use this bridge for agency joins; do not naïvely join incident.agency_ids to agencies.",
    },
    {
        "table": "state_population",
        "field": "population",
        "definition": "Annual Census Population Estimates Program resident population, July 1 estimates unless Census documentation specifies base values.",
    },
    {
        "table": "state_year_rates",
        "field": "fatal_shootings_per_1m",
        "definition": "fatal_shootings / state population * 1,000,000.",
    },
    {
        "table": "state_overall_rates",
        "field": "annualized_fatal_shootings_per_1m",
        "definition": "2015-2024 fatal shooting count divided by average 2015-2024 state population and 10 years, then multiplied by 1,000,000.",
    },
    {
        "table": "race_year_numerator_summary",
        "field": "rate_per_1m_total_us_population_NOT_GROUP_SPECIFIC",
        "definition": "Screening metric only. Uses total U.S. population, not race-specific denominators.",
    },
]

# Write CSV helper.
def write_csv(path, rows):
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


outputs = {
    "clean_incidents": os.path.join(OUT_DIR, "clean_incidents_v2.csv"),
    "clean_agencies": os.path.join(OUT_DIR, "clean_agencies_v2.csv"),
    "incident_agency_bridge": os.path.join(OUT_DIR, "incident_agency_bridge.csv"),
    "state_population": os.path.join(OUT_DIR, "state_population_2015_2025.csv"),
    "state_year_rates": os.path.join(OUT_DIR, "state_year_rates_2015_2024.csv"),
    "national_year_rates": os.path.join(OUT_DIR, "national_year_rates_2015_2024.csv"),
    "state_overall_rates": os.path.join(OUT_DIR, "state_overall_rates_2015_2024.csv"),
    "race_year_numerator_summary": os.path.join(
        OUT_DIR, "race_year_numerator_summary.csv"
    ),
    "data_dictionary": os.path.join(OUT_DIR, "data_dictionary.csv"),
}
write_csv(outputs["clean_incidents"], clean_incidents)
write_csv(outputs["clean_agencies"], clean_agencies)
write_csv(outputs["incident_agency_bridge"], bridge_rows)
write_csv(outputs["state_population"], pop_rows)
write_csv(outputs["state_year_rates"], state_year_rows)
write_csv(outputs["national_year_rates"], national_rows)
write_csv(outputs["state_overall_rates"], state_overall_rows)
write_csv(outputs["race_year_numerator_summary"], race_year_rows)
write_csv(outputs["data_dictionary"], data_dictionary)

# Quality checks.
checks = {
    "incident_rows": len(clean_incidents),
    "agency_rows": len(clean_agencies),
    "incident_agency_bridge_rows": len(bridge_rows),
    "multi_agency_incidents": sum(1 for r in clean_incidents if r["agency_count"] > 1),
    "state_population_rows": len(pop_rows),
    "state_year_rate_rows": len(state_year_rows),
    "national_year_rows": len(national_rows),
    "years_in_incidents": sorted(set(r["year"] for r in clean_incidents)),
    "missing_population_state_year_rows": sum(
        1 for r in state_year_rows if r["population"] == ""
    ),
    "date_min": min(r["incident_date"] for r in clean_incidents),
    "date_max": max(r["incident_date"] for r in clean_incidents),
    "top_10_states_by_annualized_rate_per_1m": state_overall_rows[:10],
    "national_rates": national_rows,
}
with open(os.path.join(OUT_DIR, "quality_checks.json"), "w", encoding="utf-8") as f:
    json.dump(checks, f, indent=2)

print(json.dumps(checks, indent=2)[:4000])
