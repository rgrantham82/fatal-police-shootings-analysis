# New Mexico Fatal Police Shooting Outlier Analysis

## Executive finding

New Mexico remains the strongest state-level outlier in the 2015-2024 fatal police shooting data. It recorded **219 fatal police shootings** with an average population of about **2,105,700**, for an annualized rate of **10.40 per 1M residents** and rank **#1** among states.

Against the rest-of-U.S. population-adjusted rate, New Mexico would have been expected to record about **65.6** fatal police shootings. It recorded **219**, a residual of **+153.4** and a standardized residual of **18.9**. That is not a tiny-denominator hiccup; it is a freight train in statistical shoes.

## Rate-ratio tests

| Comparison | NM rate / comparator rate | 95% CI | p-value |
|---|---:|---:|---:|
| NM vs rest of U.S. | 3.34x | 2.92-3.82 | 0 |
| NM vs West excluding NM | 2.40x | 2.09-2.75 | 0 |

## Region/year population-offset model

I fitted a Poisson count model using state-year fatal shooting counts with log(population) as an offset and predictors for Census region, year trend, and a New Mexico indicator. In that model, the New Mexico indicator has an incident-rate ratio of **2.40** with a 95% CI of **2.09-2.75** and p-value **5.23e-36**.

A separate region/year-only model expected **94.8** fatal shootings for NM over 2015-2024. The observed total was **219**, leaving a residual of **+124.2** and standardized residual **12.8** even after controlling for broad region and national year trend.

Poisson overdispersion ratio: **2.90**. Because this is overdispersed count data, the negative-binomial sensitivity model is included in the output package.

## Incident-profile comparison: NM vs rest of U.S.

| Factor | NM share | Rest U.S. share | Difference | Fisher p |
|---|---:|---:|---:|---:|
| Armed with gun | 67.1% | 58.8% | +8.3 pp | 0.01492 |
| Body camera indicated | 17.8% | 17.2% | +0.6 pp | 0.7869 |
| Unarmed | 5.5% | 5.4% | +0.1 pp | 0.8805 |
| Armed status unknown/undetermined | 5.5% | 6.0% | -0.6 pp | 0.8857 |
| Armed with vehicle | 3.7% | 4.3% | -0.6 pp | 0.8649 |
| Mental illness-related flag | 16.0% | 19.8% | -3.8 pp | 0.1702 |
| Race known | 80.4% | 88.8% | -8.4 pp | 0.0003338 |

## New Mexico city concentration

| City | Fatal shootings | Share of NM total | Gun-involved | Unarmed | Mental illness flag |
|---|---:|---:|---:|---:|---:|
| Albuquerque | 77 | 35.2% | 51 | 6 | 15 |
| Las Cruces | 20 | 9.1% | 12 | 1 | 7 |
| Roswell | 11 | 5.0% | 9 | 0 | 1 |
| Farmington | 10 | 4.6% | 7 | 1 | 0 |
| Santa Fe | 9 | 4.1% | 6 | 0 | 3 |
| Los Lunas | 7 | 3.2% | 4 | 2 | 1 |
| Deming | 5 | 2.3% | 4 | 0 | 1 |
| Hobbs | 5 | 2.3% | 5 | 0 | 1 |

## Interpretation

The best current explanation from the available project data is that NM's outlier rate is driven primarily by **overall elevated fatal police shooting exposure**, not by an unusually high unarmed share. NM's unarmed share is close to the national/rest-of-U.S. baseline, while its total rate is dramatically higher. The profile points toward a higher armed/gun-involved encounter environment plus geographic and institutional concentration.

The next strongest data-science step is to merge state-year external predictors: violent crime rate, firearm mortality/gun prevalence proxy, poverty, unemployment, rurality/population density, mental-health provider shortage, and police staffing. Then rerun a negative-binomial model with population offset and test whether NM remains a positive residual.

## Files included

- `state_rate_outliers_vs_rest_us.csv`
- `nm_rate_ratio_tests.csv`
- `nm_incident_profile_vs_rest_us.csv`
- `nm_categorical_distribution_tests.csv`
- `nm_city_concentration.csv`
- `nm_county_concentration.csv`
- `nm_year_trend_vs_national.csv`
- `poisson_region_year_nm_indicator_results.csv`
- `negative_binomial_region_year_nm_indicator_results.csv` if model converged
- `state_residuals_after_region_year_poisson.csv`
- `figures/` with seven PNGs

## Data caveats

- This analysis uses the project dataset already cleaned from the uploaded Washington Post Fatal Force data and merged state population estimates.
- This is observational analysis, not causal identification.
- Some variables, especially race, mental-health status, and threat/armed coding, may be incomplete or inconsistently coded.
- City/county counts are not per capita because city/county denominators were not yet merged.
