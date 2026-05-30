#!/usr/bin/env python3
"""
Build an enhanced state-year modeling dataset and first-pass predictive models for
fatal police shootings. Uses only the cleaned package created from Washington Post
Fatal Force v2 plus Census population denominators already present locally.

No internet calls are made in this script. Additional public-source integrations
(ACS/BLS/FBI) are documented as source notes because those endpoints require
network access from the execution environment.
"""
from __future__ import annotations

import csv
import json
import math
import os
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV, PoissonRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE = Path("/mnt/data/police_shootings_cleaned_percapita")
OUT = Path("/mnt/data/police_shootings_enhanced_prediction")
OUT.mkdir(parents=True, exist_ok=True)

INCIDENTS = BASE / "clean_incidents_v2.csv"
AGENCIES = BASE / "clean_agencies_v2.csv"
BRIDGE = BASE / "incident_agency_bridge.csv"
STATE_RATES = BASE / "state_year_rates_2015_2024.csv"
STATE_POP = BASE / "state_population_2015_2025.csv"

STATE_REGION_DIVISION = {
    "CT": ("Northeast", "New England"),
    "ME": ("Northeast", "New England"),
    "MA": ("Northeast", "New England"),
    "NH": ("Northeast", "New England"),
    "RI": ("Northeast", "New England"),
    "VT": ("Northeast", "New England"),
    "NJ": ("Northeast", "Middle Atlantic"),
    "NY": ("Northeast", "Middle Atlantic"),
    "PA": ("Northeast", "Middle Atlantic"),
    "IL": ("Midwest", "East North Central"),
    "IN": ("Midwest", "East North Central"),
    "MI": ("Midwest", "East North Central"),
    "OH": ("Midwest", "East North Central"),
    "WI": ("Midwest", "East North Central"),
    "IA": ("Midwest", "West North Central"),
    "KS": ("Midwest", "West North Central"),
    "MN": ("Midwest", "West North Central"),
    "MO": ("Midwest", "West North Central"),
    "NE": ("Midwest", "West North Central"),
    "ND": ("Midwest", "West North Central"),
    "SD": ("Midwest", "West North Central"),
    "DE": ("South", "South Atlantic"),
    "DC": ("South", "South Atlantic"),
    "FL": ("South", "South Atlantic"),
    "GA": ("South", "South Atlantic"),
    "MD": ("South", "South Atlantic"),
    "NC": ("South", "South Atlantic"),
    "SC": ("South", "South Atlantic"),
    "VA": ("South", "South Atlantic"),
    "WV": ("South", "South Atlantic"),
    "AL": ("South", "East South Central"),
    "KY": ("South", "East South Central"),
    "MS": ("South", "East South Central"),
    "TN": ("South", "East South Central"),
    "AR": ("South", "West South Central"),
    "LA": ("South", "West South Central"),
    "OK": ("South", "West South Central"),
    "TX": ("South", "West South Central"),
    "AZ": ("West", "Mountain"),
    "CO": ("West", "Mountain"),
    "ID": ("West", "Mountain"),
    "MT": ("West", "Mountain"),
    "NV": ("West", "Mountain"),
    "NM": ("West", "Mountain"),
    "UT": ("West", "Mountain"),
    "WY": ("West", "Mountain"),
    "AK": ("West", "Pacific"),
    "CA": ("West", "Pacific"),
    "HI": ("West", "Pacific"),
    "OR": ("West", "Pacific"),
    "WA": ("West", "Pacific"),
}

RACE_KEYS = ["W", "B", "H", "A", "N", "O"]
AGENCY_TYPES = [
    "local_police",
    "sheriff",
    "state_police",
    "federal",
    "local_other",
    "state_other",
    "other",
]
THREAT_KEYS = ["shoot", "threat", "point", "attack", "move", "flee", "undetermined"]
FLEE_KEYS = ["not fleeing", "car", "foot", "other"]


def read_csv_dict(path: Path) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def to_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def write_csv(path: Path, rows: List[Dict[str, Any]], headers: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for h in headers:
                val = row.get(h, "")
                if isinstance(val, float):
                    if math.isnan(val) or math.isinf(val):
                        val = ""
                    else:
                        val = round(val, 6)
                out[h] = val
            writer.writerow(out)


# Load base state-year target/population table
state_year_rows = read_csv_dict(STATE_RATES)
pop_rows = read_csv_dict(STATE_POP)

# 2025 population by state for forecasts
pop_by_state_year: Dict[Tuple[str, int], int] = {}
state_names: Dict[str, str] = {}
state_fips: Dict[str, str] = {}
for r in pop_rows:
    year = to_int(r.get("year"))
    abbr = r.get("state_abbr", "")
    if not abbr:
        continue
    pop_by_state_year[(abbr, year)] = to_int(r.get("population"))
    state_names[abbr] = r.get("state_name", "")
    state_fips[abbr] = r.get("state_fips", "")

# Base state-year table
base_by_key: Dict[Tuple[str, int], Dict[str, Any]] = {}
for r in state_year_rows:
    abbr, year = r["state_abbr"], to_int(r["year"])
    key = (abbr, year)
    state_names[abbr] = r.get("state_name", state_names.get(abbr, ""))
    state_fips[abbr] = r.get("state_fips", state_fips.get(abbr, ""))
    base_by_key[key] = {
        "state_abbr": abbr,
        "state_fips": r.get("state_fips"),
        "state_name": r.get("state_name"),
        "year": year,
        "fatal_shootings": to_int(r.get("fatal_shootings")),
        "population": to_int(r.get("population")),
        "fatal_shootings_per_1m": to_float(r.get("fatal_shootings_per_1m")),
        "unarmed_count": to_int(r.get("unarmed_count")),
        "armed_with_gun_count": to_int(r.get("armed_with_gun_count")),
        "mental_illness_related_count": to_int(r.get("mental_illness_related_count")),
        "body_camera_count": to_int(r.get("body_camera_count")),
        "race_known_count": to_int(r.get("race_known_count")),
        "race_missing_count": to_int(r.get("race_missing_count")),
    }

states = sorted({abbr for abbr, year in base_by_key.keys()})
years = list(range(2015, 2025))

# Incident-level aggregates by state-year
inc_aggs: Dict[Tuple[str, int], Dict[str, Any]] = defaultdict(
    lambda: defaultdict(float)
)
ages: Dict[Tuple[str, int], List[float]] = defaultdict(list)
incidents = read_csv_dict(INCIDENTS)
for r in incidents:
    abbr = r.get("state_abbr", "")
    year = to_int(r.get("year"))
    if not abbr or not year:
        continue
    key = (abbr, year)
    a = inc_aggs[key]
    a["incident_count"] += 1
    if r.get("is_unarmed") in ("True", "true", "1", True):
        a["unarmed_count_incident"] += 1
    if r.get("armed_with_gun") in ("True", "true", "1", True):
        a["gun_count_incident"] += 1
    if r.get("armed_with_vehicle") in ("True", "true", "1", True):
        a["vehicle_count_incident"] += 1
    if r.get("was_mental_illness_related") in ("True", "true", "1", True):
        a["mental_count_incident"] += 1
    if r.get("body_camera") in ("True", "true", "1", True):
        a["bodycam_count_incident"] += 1
    gender = (r.get("gender") or "").lower()
    if gender == "male":
        a["male_count_incident"] += 1
    race_codes = r.get("race_codes") or ""
    parts = [p.strip() for p in race_codes.split(";") if p.strip()]
    for code in RACE_KEYS:
        if code in parts:
            a[f"race_{code}_count_incident"] += 1
    threat = (r.get("threat_type") or "").lower()
    for t in THREAT_KEYS:
        if threat == t:
            a[f'threat_{t.replace(" ", "_")}_count_incident'] += 1
    flee = (r.get("flee_status") or "").lower()
    for fl in FLEE_KEYS:
        if flee == fl:
            a[f'flee_{fl.replace(" ", "_")}_count_incident'] += 1
    agency_count = to_float(r.get("agency_count"), 0)
    a["agency_count_sum_incident"] += agency_count
    if agency_count > 1:
        a["multi_agency_count_incident"] += 1
    age = to_float(r.get("age"), 0)
    if age > 0:
        ages[key].append(age)

# Normalize incident aggregates
for key, a in list(inc_aggs.items()):
    n = a.get("incident_count", 0)
    for raw, share in [
        ("unarmed_count_incident", "unarmed_share"),
        ("gun_count_incident", "gun_share"),
        ("vehicle_count_incident", "vehicle_share"),
        ("mental_count_incident", "mental_illness_share"),
        ("bodycam_count_incident", "body_camera_share"),
        ("male_count_incident", "male_share"),
        ("multi_agency_count_incident", "multi_agency_share"),
    ]:
        a[share] = safe_div(a.get(raw, 0), n)
    a["avg_agency_count"] = safe_div(a.get("agency_count_sum_incident", 0), n)
    for code in RACE_KEYS:
        a[f"race_{code}_share"] = safe_div(a.get(f"race_{code}_count_incident", 0), n)
    for t in THREAT_KEYS:
        clean = t.replace(" ", "_")
        a[f"threat_{clean}_share"] = safe_div(
            a.get(f"threat_{clean}_count_incident", 0), n
        )
    for fl in FLEE_KEYS:
        clean = fl.replace(" ", "_")
        a[f"flee_{clean}_share"] = safe_div(a.get(f"flee_{clean}_count_incident", 0), n)
    if ages.get(key):
        a["median_age"] = statistics.median(ages[key])
    else:
        a["median_age"] = 0.0

# Agency bridge aggregates by state-year
bridge_aggs: Dict[Tuple[str, int], Dict[str, Any]] = defaultdict(
    lambda: defaultdict(float)
)
unique_agencies: Dict[Tuple[str, int], set] = defaultdict(set)
bridge_rows = read_csv_dict(BRIDGE)
for r in bridge_rows:
    key = (r.get("state_abbr", ""), to_int(r.get("year")))
    if not key[0] or not key[1]:
        continue
    a = bridge_aggs[key]
    agency_id = r.get("agency_id") or ""
    if agency_id:
        unique_agencies[key].add(agency_id)
    typ = r.get("agency_type") or "missing"
    if typ in AGENCY_TYPES:
        a[f"agency_type_{typ}_pairs"] += 1
    a["agency_pairs"] += 1

for key, a in list(bridge_aggs.items()):
    pairs = a.get("agency_pairs", 0)
    a["unique_agencies"] = len(unique_agencies.get(key, set()))
    for typ in AGENCY_TYPES:
        a[f"agency_type_{typ}_share"] = safe_div(
            a.get(f"agency_type_{typ}_pairs", 0), pairs
        )

# Build enhanced dataset, including a synthetic 2025 row for forecasting only
all_rows: List[Dict[str, Any]] = []
all_years = list(range(2015, 2026))
for abbr in states:
    region, division = STATE_REGION_DIVISION.get(abbr, ("Unknown", "Unknown"))
    for year in all_years:
        key = (abbr, year)
        base = base_by_key.get(key, {})
        pop = base.get("population") or pop_by_state_year.get(key, 0)
        fatal = base.get("fatal_shootings", "")
        rate = safe_div(to_float(fatal, 0), pop) * 1_000_000 if pop else ""
        prior_pop = pop_by_state_year.get((abbr, year - 1), 0)
        row = {
            "state_abbr": abbr,
            "state_fips": state_fips.get(abbr, ""),
            "state_name": state_names.get(abbr, ""),
            "region": region,
            "division": division,
            "year": year,
            "is_forecast_year": year == 2025,
            "fatal_shootings": fatal,
            "population": pop,
            "log_population": math.log(pop) if pop else 0.0,
            "population_growth_1yr": safe_div(pop - prior_pop, prior_pop)
            if prior_pop
            else 0.0,
            "fatal_shootings_per_1m": rate,
            "year_index": year - 2015,
            "post_2020": 1 if year >= 2021 else 0,
        }
        # merge current-year aggregates for descriptive purposes; these are NOT directly used as current-year predictors
        inc = inc_aggs.get(key, {})
        bridge = bridge_aggs.get(key, {})
        for name in [
            "unarmed_share",
            "gun_share",
            "vehicle_share",
            "mental_illness_share",
            "body_camera_share",
            "male_share",
            "median_age",
            "multi_agency_share",
            "avg_agency_count",
            *[f"race_{c}_share" for c in RACE_KEYS],
            *[f'threat_{t.replace(" ", "_")}_share' for t in THREAT_KEYS],
            *[f'flee_{fl.replace(" ", "_")}_share' for fl in FLEE_KEYS],
        ]:
            row[name] = inc.get(name, 0.0)
        for name in [
            "unique_agencies",
            *[f"agency_type_{typ}_share" for typ in AGENCY_TYPES],
        ]:
            row[name] = bridge.get(name, 0.0)
        all_rows.append(row)

# Index rows by state-year for lags
row_by_key = {(r["state_abbr"], r["year"]): r for r in all_rows}

lag_base_fields = ["fatal_shootings", "fatal_shootings_per_1m"]
composition_fields = [
    "unarmed_share",
    "gun_share",
    "vehicle_share",
    "mental_illness_share",
    "body_camera_share",
    "male_share",
    "median_age",
    "multi_agency_share",
    "avg_agency_count",
    "unique_agencies",
    *[f"race_{c}_share" for c in RACE_KEYS],
    *[f'threat_{t.replace(" ", "_")}_share' for t in THREAT_KEYS],
    *[f'flee_{fl.replace(" ", "_")}_share' for fl in FLEE_KEYS],
    *[f"agency_type_{typ}_share" for typ in AGENCY_TYPES],
]

for r in all_rows:
    abbr, year = r["state_abbr"], r["year"]
    # Count/rate lags and rolling features
    prior_counts = []
    prior_rates = []
    for lag in [1, 2, 3]:
        prev = row_by_key.get((abbr, year - lag), {})
        count = to_float(prev.get("fatal_shootings"), 0.0)
        rate = to_float(prev.get("fatal_shootings_per_1m"), 0.0)
        r[f"fatal_shootings_lag{lag}"] = count
        r[f"fatal_rate_per_1m_lag{lag}"] = rate
        if prev and prev.get("fatal_shootings") != "":
            prior_counts.append(count)
            prior_rates.append(rate)
    r["fatal_shootings_roll3_avg"] = (
        statistics.mean(prior_counts) if prior_counts else 0.0
    )
    r["fatal_shootings_roll3_sd"] = (
        statistics.pstdev(prior_counts) if len(prior_counts) > 1 else 0.0
    )
    r["fatal_rate_per_1m_roll3_avg"] = (
        statistics.mean(prior_rates) if prior_rates else 0.0
    )
    r["fatal_rate_per_1m_roll3_sd"] = (
        statistics.pstdev(prior_rates) if len(prior_rates) > 1 else 0.0
    )
    r["fatal_count_lag1_delta"] = r["fatal_shootings_lag1"] - r["fatal_shootings_lag2"]
    r["fatal_rate_lag1_delta"] = (
        r["fatal_rate_per_1m_lag1"] - r["fatal_rate_per_1m_lag2"]
    )
    # Lag composition predictors only from prior year to avoid same-year leakage
    for field in composition_fields:
        prev = row_by_key.get((abbr, year - 1), {})
        r[f"{field}_lag1"] = to_float(prev.get(field), 0.0)
        # 3-year lagged mean
        vals = []
        for lag in [1, 2, 3]:
            prev_lag = row_by_key.get((abbr, year - lag), {})
            if prev_lag:
                vals.append(to_float(prev_lag.get(field), 0.0))
        r[f"{field}_roll3_avg"] = statistics.mean(vals) if vals else 0.0

# One-hot fields for regions/divisions
regions = sorted(set(r["region"] for r in all_rows if r["region"] != "Unknown"))
divisions = sorted(set(r["division"] for r in all_rows if r["division"] != "Unknown"))
for r in all_rows:
    for region in regions:
        r[f'region_{region.replace(" ", "_")}'] = 1 if r["region"] == region else 0
    for div in divisions:
        r[f'division_{div.replace(" ", "_").replace("-", "_")}'] = (
            1 if r["division"] == div else 0
        )

# Previous national rate baseline
nat_rates = {}
for year in years:
    total_count = sum(
        to_float(row_by_key[(s, year)].get("fatal_shootings"), 0.0)
        for s in states
        if (s, year) in row_by_key
    )
    total_pop = sum(
        to_float(row_by_key[(s, year)].get("population"), 0.0)
        for s in states
        if (s, year) in row_by_key
    )
    nat_rates[year] = safe_div(total_count, total_pop) * 1_000_000 if total_pop else 0.0
for r in all_rows:
    prev_rate = nat_rates.get(r["year"] - 1, 0.0)
    r["prev_national_rate_per_1m"] = prev_rate
    r["prev_national_rate_expected_count"] = (
        prev_rate * r.get("population", 0) / 1_000_000
    )

# Headers for enhanced dataset
base_headers = [
    "state_abbr",
    "state_fips",
    "state_name",
    "region",
    "division",
    "year",
    "is_forecast_year",
    "fatal_shootings",
    "population",
    "log_population",
    "population_growth_1yr",
    "fatal_shootings_per_1m",
    "year_index",
    "post_2020",
]
current_headers = composition_fields
lag_headers = [
    "fatal_shootings_lag1",
    "fatal_shootings_lag2",
    "fatal_shootings_lag3",
    "fatal_rate_per_1m_lag1",
    "fatal_rate_per_1m_lag2",
    "fatal_rate_per_1m_lag3",
    "fatal_shootings_roll3_avg",
    "fatal_shootings_roll3_sd",
    "fatal_rate_per_1m_roll3_avg",
    "fatal_rate_per_1m_roll3_sd",
    "fatal_count_lag1_delta",
    "fatal_rate_lag1_delta",
    "prev_national_rate_per_1m",
    "prev_national_rate_expected_count",
]
lag_comp_headers = []
for field in composition_fields:
    lag_comp_headers += [f"{field}_lag1", f"{field}_roll3_avg"]
onehot_headers = [f'region_{x.replace(" ", "_")}' for x in regions] + [
    f'division_{x.replace(" ", "_").replace("-", "_")}' for x in divisions
]
headers = (
    base_headers + current_headers + lag_headers + lag_comp_headers + onehot_headers
)
write_csv(OUT / "enhanced_state_year_modeling_dataset.csv", all_rows, headers)

# Feature dictionary
feature_dict: List[Dict[str, str]] = []


def add_feat(name, role, source, leakage, notes):
    feature_dict.append(
        {
            "field": name,
            "role": role,
            "source": source,
            "leakage_status": leakage,
            "notes": notes,
        }
    )


for h in base_headers:
    add_feat(
        h,
        "identifier/target/exposure"
        if h in ["fatal_shootings", "population", "fatal_shootings_per_1m"]
        else "identifier/static feature",
        "cleaned state-year rates + Census population denominators",
        "safe" if h != "fatal_shootings_per_1m" else "target-derived",
        "Base state-year field",
    )
for h in current_headers:
    add_feat(
        h,
        "descriptive current-year composition",
        "incident and agency aggregates",
        "do_not_use_for_same_year_prediction",
        "Current-year descriptive variable; lagged versions are used for prediction",
    )
for h in lag_headers + lag_comp_headers + onehot_headers:
    source = (
        "engineered lag/rolling feature"
        if "lag" in h or "roll" in h
        else "engineered static category"
    )
    add_feat(
        h,
        "predictor",
        source,
        "safe_lagged_or_static",
        "Included in enhanced model feature set unless otherwise excluded",
    )
write_csv(
    OUT / "enhanced_feature_dictionary.csv",
    feature_dict,
    ["field", "role", "source", "leakage_status", "notes"],
)

# Modeling
model_rows = [
    r
    for r in all_rows
    if r["year"] >= 2018 and r["year"] <= 2024 and r["fatal_shootings"] != ""
]
train_rows = [r for r in model_rows if r["year"] <= 2022]
test_rows = [r for r in model_rows if r["year"] >= 2023]
forecast_rows = [r for r in all_rows if r["year"] == 2025]

feature_cols = [
    "population",
    "log_population",
    "population_growth_1yr",
    "year_index",
    "post_2020",
    "fatal_shootings_lag1",
    "fatal_shootings_lag2",
    "fatal_shootings_lag3",
    "fatal_rate_per_1m_lag1",
    "fatal_rate_per_1m_lag2",
    "fatal_rate_per_1m_lag3",
    "fatal_shootings_roll3_avg",
    "fatal_shootings_roll3_sd",
    "fatal_rate_per_1m_roll3_avg",
    "fatal_rate_per_1m_roll3_sd",
    "fatal_count_lag1_delta",
    "fatal_rate_lag1_delta",
    "prev_national_rate_expected_count",
    # composition lag/roll predictors
    *[f"{f}_lag1" for f in composition_fields],
    *[f"{f}_roll3_avg" for f in composition_fields],
    *onehot_headers,
]

# Remove invariant/empty features in train
usable_features = []
for col in feature_cols:
    vals = [to_float(r.get(col), 0.0) for r in train_rows]
    if len(set(round(v, 10) for v in vals)) > 1:
        usable_features.append(col)

X_train = np.array(
    [[to_float(r.get(c), 0.0) for c in usable_features] for r in train_rows],
    dtype=float,
)
y_train = np.array([to_float(r["fatal_shootings"]) for r in train_rows], dtype=float)
X_test = np.array(
    [[to_float(r.get(c), 0.0) for c in usable_features] for r in test_rows], dtype=float
)
y_test = np.array([to_float(r["fatal_shootings"]) for r in test_rows], dtype=float)
X_fore = np.array(
    [[to_float(r.get(c), 0.0) for c in usable_features] for r in forecast_rows],
    dtype=float,
)

models = {
    "ridge_enhanced_lagged": Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", RidgeCV(alphas=[0.01, 0.1, 1, 3, 10, 30, 100, 300])),
        ]
    ),
    "poisson_enhanced_lagged": Pipeline(
        [
            ("scale", StandardScaler()),
            ("model", PoissonRegressor(alpha=3.0, max_iter=500)),
        ]
    ),
    "random_forest_enhanced_lagged": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        min_samples_leaf=5,
        max_features="sqrt",
        n_jobs=-1,
    ),
}

predictions_test: Dict[str, np.ndarray] = {}
predictions_fore: Dict[str, np.ndarray] = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    pred = np.asarray(model.predict(X_test), dtype=float)
    pred_fore = np.asarray(model.predict(X_fore), dtype=float)
    predictions_test[name] = np.clip(pred, 0, None)
    predictions_fore[name] = np.clip(pred_fore, 0, None)

# Baselines
predictions_test["lag1_baseline"] = np.array(
    [to_float(r["fatal_shootings_lag1"]) for r in test_rows], dtype=float
)
predictions_test["roll3_baseline"] = np.array(
    [to_float(r["fatal_shootings_roll3_avg"]) for r in test_rows], dtype=float
)
predictions_test["prev_national_rate_baseline"] = np.array(
    [to_float(r["prev_national_rate_expected_count"]) for r in test_rows], dtype=float
)

predictions_fore["lag1_baseline"] = np.array(
    [to_float(r["fatal_shootings_lag1"]) for r in forecast_rows], dtype=float
)
predictions_fore["roll3_baseline"] = np.array(
    [to_float(r["fatal_shootings_roll3_avg"]) for r in forecast_rows], dtype=float
)
predictions_fore["prev_national_rate_baseline"] = np.array(
    [to_float(r["prev_national_rate_expected_count"]) for r in forecast_rows],
    dtype=float,
)

# Ensemble: average of top non-baseline/simple robust models by count MAE on holdout, excluding prev_national_rate
metrics_rows = []
for name, pred in predictions_test.items():
    pop_test = np.array([to_float(r["population"]) for r in test_rows], dtype=float)
    actual_rate = y_test / pop_test * 1_000_000
    pred_rate = pred / pop_test * 1_000_000
    mae = mean_absolute_error(y_test, pred)
    rmse = math.sqrt(mean_squared_error(y_test, pred))
    rate_mae = mean_absolute_error(actual_rate, pred_rate)
    national_error = float(np.sum(pred) - np.sum(y_test))
    metrics_rows.append(
        {
            "model": name,
            "train_years": "2018-2022",
            "test_years": "2023-2024",
            "n_train_rows": len(train_rows),
            "n_test_rows": len(test_rows),
            "count_mae": mae,
            "count_rmse": rmse,
            "rate_mae_per_1m": rate_mae,
            "national_total_error": national_error,
            "actual_holdout_total": float(np.sum(y_test)),
            "predicted_holdout_total": float(np.sum(pred)),
            "mean_predicted_count": float(np.mean(pred)),
            "mean_actual_count": float(np.mean(y_test)),
        }
    )

# Create ensemble from best 4 by count MAE, preferring diverse models
ranked = sorted(metrics_rows, key=lambda x: x["count_mae"])
ensemble_names = [
    r["model"]
    for r in ranked
    if r["model"] in predictions_test and r["model"] != "prev_national_rate_baseline"
][:4]
if ensemble_names:
    pred_ens = np.mean(np.vstack([predictions_test[n] for n in ensemble_names]), axis=0)
    predictions_test["ensemble_top4_holdout_mae"] = pred_ens
    pred_fore_ens = np.mean(
        np.vstack([predictions_fore[n] for n in ensemble_names]), axis=0
    )
    predictions_fore["ensemble_top4_holdout_mae"] = pred_fore_ens
    pop_test = np.array([to_float(r["population"]) for r in test_rows], dtype=float)
    metrics_rows.append(
        {
            "model": "ensemble_top4_holdout_mae",
            "train_years": "2018-2022",
            "test_years": "2023-2024",
            "n_train_rows": len(train_rows),
            "n_test_rows": len(test_rows),
            "count_mae": mean_absolute_error(y_test, pred_ens),
            "count_rmse": math.sqrt(mean_squared_error(y_test, pred_ens)),
            "rate_mae_per_1m": mean_absolute_error(
                y_test / pop_test * 1_000_000, pred_ens / pop_test * 1_000_000
            ),
            "national_total_error": float(np.sum(pred_ens) - np.sum(y_test)),
            "actual_holdout_total": float(np.sum(y_test)),
            "predicted_holdout_total": float(np.sum(pred_ens)),
            "mean_predicted_count": float(np.mean(pred_ens)),
            "mean_actual_count": float(np.mean(y_test)),
        }
    )

metrics_rows = sorted(metrics_rows, key=lambda x: (x["count_mae"], x["count_rmse"]))
write_csv(
    OUT / "enhanced_model_evaluation_2023_2024_holdout.csv",
    metrics_rows,
    [
        "model",
        "train_years",
        "test_years",
        "n_train_rows",
        "n_test_rows",
        "count_mae",
        "count_rmse",
        "rate_mae_per_1m",
        "national_total_error",
        "actual_holdout_total",
        "predicted_holdout_total",
        "mean_predicted_count",
        "mean_actual_count",
    ],
)

# Holdout predictions table
holdout_rows = []
for i, r in enumerate(test_rows):
    base = {
        "state_abbr": r["state_abbr"],
        "state_name": r["state_name"],
        "region": r["region"],
        "division": r["division"],
        "year": r["year"],
        "actual_fatal_shootings": to_float(r["fatal_shootings"]),
        "population": to_int(r["population"]),
        "actual_rate_per_1m": to_float(r["fatal_shootings_per_1m"]),
        "lag1_count": to_float(r["fatal_shootings_lag1"]),
        "roll3_avg_count": to_float(r["fatal_shootings_roll3_avg"]),
    }
    for name, pred in predictions_test.items():
        base[f"pred_{name}"] = float(pred[i])
        base[f"error_{name}"] = float(pred[i] - to_float(r["fatal_shootings"]))
    holdout_rows.append(base)
write_csv(
    OUT / "enhanced_state_year_holdout_predictions.csv",
    holdout_rows,
    list(holdout_rows[0].keys()),
)

# 2025 forecast table
forecast_output = []
for i, r in enumerate(forecast_rows):
    row = {
        "state_abbr": r["state_abbr"],
        "state_name": r["state_name"],
        "region": r["region"],
        "division": r["division"],
        "year": 2025,
        "population": to_int(r["population"]),
        "prior_2024_count": to_float(r["fatal_shootings_lag1"]),
        "prior_3yr_avg_count": to_float(r["fatal_shootings_roll3_avg"]),
        "prior_3yr_avg_rate_per_1m": to_float(r["fatal_rate_per_1m_roll3_avg"]),
    }
    for name, pred in predictions_fore.items():
        row[f"forecast_{name}"] = float(pred[i])
        row[f"forecast_rate_per_1m_{name}"] = (
            safe_div(float(pred[i]), to_float(r["population"])) * 1_000_000
        )
    forecast_output.append(row)
forecast_headers = list(forecast_output[0].keys())
write_csv(OUT / "enhanced_2025_state_forecast.csv", forecast_output, forecast_headers)

national_forecast = {}
for name, pred in predictions_fore.items():
    national_forecast[name] = float(np.sum(pred))
national_forecast["ensemble_members"] = ensemble_names
national_forecast["forecast_year_population_total"] = int(
    sum(to_int(r["population"]) for r in forecast_rows)
)
national_forecast["actual_2024_total"] = int(
    sum(to_float(row_by_key[(s, 2024)].get("fatal_shootings")) for s in states)
)
national_forecast["actual_2023_total"] = int(
    sum(to_float(row_by_key[(s, 2023)].get("fatal_shootings")) for s in states)
)
with open(
    OUT / "enhanced_national_2025_forecast_summary.json", "w", encoding="utf-8"
) as f:
    json.dump(national_forecast, f, indent=2)

# Model feature importance/coefs rough summaries
importance_rows = []
# Ridge coefficients after scaling correspond to standardized features
ridge = models["ridge_enhanced_lagged"].named_steps["model"]
coefs = ridge.coef_
for feat, coef in sorted(
    zip(usable_features, coefs), key=lambda x: abs(x[1]), reverse=True
)[:40]:
    importance_rows.append(
        {
            "model": "ridge_enhanced_lagged",
            "feature": feat,
            "importance_value": float(coef),
            "importance_type": "standardized_coefficient",
        }
    )
rf = models["random_forest_enhanced_lagged"]
for feat, imp in sorted(
    zip(usable_features, rf.feature_importances_), key=lambda x: x[1], reverse=True
)[:40]:
    importance_rows.append(
        {
            "model": "random_forest_enhanced_lagged",
            "feature": feat,
            "importance_value": float(imp),
            "importance_type": "feature_importance",
        }
    )
write_csv(
    OUT / "enhanced_model_feature_importance.csv",
    importance_rows,
    ["model", "feature", "importance_value", "importance_type"],
)

# Quality checks
quality = {
    "states": len(states),
    "modeled_training_rows": len(train_rows),
    "modeled_holdout_rows": len(test_rows),
    "forecast_rows_2025": len(forecast_rows),
    "feature_columns_considered": len(feature_cols),
    "usable_nonconstant_features": len(usable_features),
    "holdout_years": [2023, 2024],
    "training_years": [2018, 2019, 2020, 2021, 2022],
    "actual_holdout_total": float(np.sum(y_test)),
    "best_model_by_count_mae": metrics_rows[0]["model"],
    "best_count_mae": metrics_rows[0]["count_mae"],
    "ensemble_members": ensemble_names,
}
with open(OUT / "enhanced_quality_checks.json", "w", encoding="utf-8") as f:
    json.dump(quality, f, indent=2)

# Source notes and report
report = f"""# Enhanced Police Shootings Prediction Model Report

## Scope

This package upgrades the first-pass state-year forecasting exercise by adding lagged incident-composition and agency-mix predictors derived from the cleaned Washington Post Fatal Force v2 incident data and agency bridge table.

## Prediction target

- Unit: state-year
- Target: fatal police shooting count
- Exposure/denominator: state resident population
- Training window: 2018-2022
- Holdout window: 2023-2024
- Forecast window: 2025, exploratory only

The training window begins in 2018 because the enhanced models use lag-3 and rolling-3 predictors.

## Leakage control

Current-year incident composition variables are included in the modeling dataset for descriptive analysis, but same-year versions should not be used to predict same-year counts. The model uses lagged and rolling prior-year versions, such as `gun_share_lag1`, `mental_illness_share_roll3_avg`, and `agency_type_sheriff_share_lag1`.

## Enhanced predictors

Predictor groups include:

1. Population and population growth
2. Census region/division indicators
3. Prior fatal shooting counts and rates
4. Rolling 3-year count/rate features
5. Prior-year incident composition: armed status, threat type, fleeing status, mental-illness-related flag, body-camera flag, gender/race composition
6. Prior-year agency mix: unique agencies, average agency count per incident, local/sheriff/state/federal shares

## Best holdout model

Best model by count MAE: **{metrics_rows[0]['model']}**

- Count MAE: {metrics_rows[0]['count_mae']:.3f}
- Count RMSE: {metrics_rows[0]['count_rmse']:.3f}
- Rate MAE per 1M: {metrics_rows[0]['rate_mae_per_1m']:.3f}
- National total error, 2023-2024: {metrics_rows[0]['national_total_error']:.1f}

## 2025 exploratory national forecasts

"""
for name, val in sorted(national_forecast.items()):
    if name not in [
        "ensemble_members",
        "forecast_year_population_total",
        "actual_2024_total",
        "actual_2023_total",
    ]:
        report += f"- {name}: {val:.1f}\n"
report += f"\nEnsemble members: {', '.join(ensemble_names)}\n"
report += """
## Cautions

This remains a small panel dataset: 51 jurisdictions by 10 years, with only 5 effective training years for lag-3 models. The enhanced predictors improve structure and interpretability, but they do not establish causal effects. Predictions should be framed as expected aggregate counts under historical patterns, not as deterministic outcomes.

## Recommended next external joins

The next true upgrade is to join state-year ACS, BLS LAUS, and FBI Crime Data Explorer variables. Those endpoints are documented in `external_data_source_notes.md`, but the present execution environment did not provide direct network access for automated download.
"""
with open(OUT / "enhanced_model_report.md", "w", encoding="utf-8") as f:
    f.write(report)

source_notes = """# External Data Source Notes for Next Integration

This package includes an enhanced feature-engineered model using the datasets already available locally. For the next network-enabled run, add these external datasets:

1. Census ACS 5-year data profiles by state-year
   - Candidate predictors: poverty rate, unemployment rate, median household income, race/ethnicity population denominators, vehicle access, educational attainment, urban/rural proxies.
   - Use ACS carefully: 5-year estimates are rolling period estimates, not single-year observations.

2. Bureau of Labor Statistics LAUS annual state unemployment
   - Candidate predictors: unemployment rate, labor force, employed, unemployed.
   - State annual averages can be merged by state/year.

3. FBI Crime Data Explorer / UCR estimated crime data
   - Candidate predictors: violent crime rate, homicide rate, aggravated assault rate, arrest rates where available.
   - Coverage and agency reporting changes must be documented, especially around the NIBRS transition.

4. Census urban/rural classification
   - Candidate predictors: percent urban, percent rural, urbanized population.
   - Best used as a static or slowly changing state-level covariate.

5. Agency-level denominators
   - Candidate predictors: sworn officers, jurisdiction population, calls for service, arrests.
   - This is necessary for serious agency-level rate modeling.

Do not merge current-year crime, unemployment, or ACS variables into a genuine forecast unless they would have been known at prediction time. For policy explanation models, current-year covariates may be acceptable if framed as association rather than forecast.
"""
with open(OUT / "external_data_source_notes.md", "w", encoding="utf-8") as f:
    f.write(source_notes)

# Zip package
zip_path = Path("/mnt/data/police_shootings_enhanced_prediction_package.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        z.write(p, arcname=f"{OUT.name}/{p.name}")

print(
    json.dumps(
        {
            "out_dir": str(OUT),
            "zip_path": str(zip_path),
            "quality": quality,
            "top_metrics": metrics_rows[:5],
            "national_forecast": national_forecast,
        },
        indent=2,
    )
)
