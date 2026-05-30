# Albuquerque Focus: Fatal Police Shootings, 2015–2024

## Scope and data

This package narrows the prior national/state work to Albuquerque, New Mexico. The base incident data are the cleaned Washington Post Fatal Force records used in the earlier project. The Post database tracks fatal shootings by on-duty police officers from January 1, 2015 through December 31, 2024, and it includes incident circumstances, armed status, mental-health indicator fields, locations, and agency involvement fields. City-level population denominators are not included in the base state panel, so this phase uses the 2024 Census QuickFacts population estimate for Albuquerque city as a constant denominator for first-pass city rates. That is acceptable for scouting, but not sufficient for a publishable final rate model.

## Key finding

Albuquerque is not just a New Mexico footnote. In the cleaned 2015–2024 data, Albuquerque city records account for **77 fatal police shootings**, or **35.2% of New Mexico's 219 total records**. Using a constant 2024 city population denominator of 560,326, Albuquerque's annualized rate is approximately **13.7 fatal shootings per 1 million residents**. That is about **1.32× the New Mexico statewide rate** and **4.35× the U.S. rate** in this dataset.

## Agency pattern

Among Albuquerque city records, **51 incidents** involve the Albuquerque Police Department, about **66.2%** of Albuquerque's fatal shooting records. The agency-count table is non-exclusive because some incidents involve multiple agencies; in plain English, one incident can wear more than one agency hat, which makes the simple totals behave like a courthouse clerk after lunch—technically correct, but liable to confuse the innocent.

The next most important local comparison is therefore **APD vs. non-APD incidents within Albuquerque**, followed by **Albuquerque vs. Bernalillo County outside Albuquerque**, if we can acquire complete city/county-level denominators and law-enforcement exposure measures.

## Incident characteristics

In Albuquerque city records:

- Gun-involved recorded armed status: **50 of 77** (64.9%).
- Unarmed recorded status: **6 of 77** (7.8%).
- Mental illness noted: **15 of 77** (19.5%).
- Body-camera field marked true: **15 of 77** (19.5%).

These fields should be treated as recorded indicators, not full truth. They depend on source reporting and coding. The dataset is a strong national incident census for fatal police shootings, but it is not a full police-contact dataset, not a use-of-force dataset, and not a denominator-rich local accountability database.

## Why Albuquerque needs its own model

The state-level model showed a persistent New Mexico effect even after region and year were controlled. The Albuquerque extraction suggests one likely reason: a large share of New Mexico's fatal police shooting burden is concentrated in and around Albuquerque/APD. This is not a proof of causation. It is a signal that the state model may be mixing local institutional history, urban/rural geography, violent-crime exposure, police-contact volume, mental-health-call exposure, armed-incident prevalence, and reporting artifacts into one statistical stew.

## Best next variables to add

The next Albuquerque-specific model should add:

1. **Exposure denominators:** calls for service, arrests, violent-crime incidents, weapons calls, domestic-violence calls, mental-health/CIT calls, and officer staffing by year.
2. **Place denominators:** annual population for Albuquerque, Bernalillo County, and surrounding comparison municipalities.
3. **Institutional variables:** APD consent-decree/reform periods, body-camera policy changes, Crisis Intervention Team and mobile crisis resources, use-of-force policy changes, and independent monitoring milestones.
4. **Comparison units:** Albuquerque vs. Las Cruces, Santa Fe, Rio Rancho, Bernalillo County Sheriff, New Mexico State Police, Phoenix, Tucson, Denver, Colorado Springs, Oklahoma City, and Tulsa.

## Files in this package

- `data/albuquerque_incident_detail_2015_2024.csv` — incident-level Albuquerque records.
- `data/albuquerque_agency_bridge_2015_2024.csv` — agency involvement rows for Albuquerque incidents.
- `data/albuquerque_yearly_metrics_2015_2024.csv` — yearly counts, APD/non-APD split, and basic features.
- `data/albuquerque_vs_nm_us_rate_summary.csv` — Albuquerque, APD, New Mexico, rest-of-New-Mexico, and U.S. rate comparisons.
- `data/albuquerque_context_feature_summary.csv` — feature shares across Albuquerque, APD-in-Albuquerque, New Mexico, and U.S.
- `figures/` — publication-ready visualizations for the Albuquerque-focused analysis.

## Cautions

City rates in this package use a constant 2024 population denominator. That is useful for a first-pass dashboard but should be replaced with annual ACS/Census city population estimates for final publication. Also, police fatal shooting counts should not be interpreted as a direct measure of police misconduct by themselves. They are an outcome count. Serious interpretation requires denominators and contextual controls, lest we build a grand statistical courthouse on a mudflat and call it marble.
