# Project Brief: Fatal Police Shootings, Per-Capita Rates, Predictive Modeling, and New Mexico / Albuquerque Focus

## Executive Summary

This project examines fatal police shootings in the United States using a cleaned version of the Washington Post Fatal Force dataset merged with population denominators. The analysis proceeds from national and state-level rate analysis to predictive modeling, statistical testing, New Mexico outlier analysis, and a focused Albuquerque package.

The main finding is that fatal police shootings are not distributed evenly by population alone. State and regional variation remains substantial after per-capita adjustment. The West has the highest median state annualized rate, and New Mexico emerges as the clearest state-level outlier. Albuquerque accounts for a large share of New Mexico's fatal police shooting records and therefore deserves separate city/agency-level investigation.

## Methods

The workflow included:

1. Cleaning and standardizing incident records.
2. Merging state-year population denominators.
3. Calculating rates per 1 million residents.
4. Comparing observed counts against population-based expected counts.
5. Running statistical tests for national trends, region differences, and residual patterns.
6. Training predictive models and evaluating holdout performance.
7. Focusing on New Mexico using count models and incident-profile comparisons.
8. Focusing on Albuquerque using city-level incident filtering and agency-involvement tables.
9. Building Excel dashboards and visualization packages.

## Key Findings

### National trends

Fatal police shooting rates showed a modest upward trend nationally. Unarmed fatal shooting rates declined during the same period.

### State variation

Observed-vs-expected analysis showed that states such as New Mexico, Alaska, Arizona, Colorado, and Oklahoma were above population-based expectation, while New York, New Jersey, Massachusetts, Pennsylvania, and Illinois were below expectation.

### Region

The West had the highest median state annualized fatal police shooting rate, followed by the South, Midwest, and Northeast.

### Predictive modeling

The ensemble model captured broad patterns and outperformed weak baselines, but recent-history baselines remained competitive. This suggests state-level fatal shooting counts have strong historical persistence.

### New Mexico

New Mexico recorded 219 fatal police shootings in the 2015-2024 window and an annualized rate of approximately 10.4 per 1 million residents. Negative binomial modeling showed that New Mexico remained significantly elevated even after adjusting for region, year, and population exposure.

### Albuquerque

Albuquerque city records accounted for 77 of New Mexico's 219 fatal police shooting records. APD appeared in 51 of those records. Albuquerque therefore appears central to understanding New Mexico's statewide outlier status, but APD-specific analysis must be separated from broader city, county, state, and federal agency involvement.

## Limitations

This project analyzes fatal police shootings, not all uses of force or all police-civilian encounters. Resident population is an imperfect denominator. Future work should add calls for service, arrests, violent-crime incidents, weapon-involved calls, mental-health calls, and officer staffing.

## Next Steps

1. Merge external structural predictors: ACS, CDC WONDER, FBI CDE, BJS LEMAS.
2. Build a negative binomial model with population offset and covariates for density, crime, firearm mortality, poverty, staffing, and region.
3. Construct an Albuquerque-specific denominator dataset using APD calls for service, arrests, officer staffing, and use-of-force reports.
4. Compare Albuquerque to peer Southwestern and Western cities.
5. Add geospatial analysis by tract, area command, and incident location.
