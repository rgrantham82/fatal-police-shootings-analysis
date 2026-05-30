# Enhanced Police Shootings Prediction Model Report

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

Best model by count MAE: **ensemble_top4_holdout_mae**

- Count MAE: 4.036
- Count RMSE: 6.128
- Rate MAE per 1M: 0.970
- National total error, 2023-2024: -110.6

## 2025 exploratory national forecasts

- ensemble_top4_holdout_mae: 1157.2
- lag1_baseline: 1175.0
- poisson_enhanced_lagged: 1000.9
- prev_national_rate_baseline: 1181.2
- random_forest_enhanced_lagged: 1168.1
- ridge_enhanced_lagged: 1140.4
- roll3_baseline: 1145.3

Ensemble members: roll3_baseline, lag1_baseline, random_forest_enhanced_lagged, ridge_enhanced_lagged

## Cautions

This remains a small panel dataset: 51 jurisdictions by 10 years, with only 5 effective training years for lag-3 models. The enhanced predictors improve structure and interpretability, but they do not establish causal effects. Predictions should be framed as expected aggregate counts under historical patterns, not as deterministic outcomes.

## Recommended next external joins

The next true upgrade is to join state-year ACS, BLS LAUS, and FBI Crime Data Explorer variables. Those endpoints are documented in `external_data_source_notes.md`, but the present execution environment did not provide direct network access for automated download.
