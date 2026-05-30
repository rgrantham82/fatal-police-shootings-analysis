# Next-Step Factor Model: New Mexico and State-Level Drivers

## Purpose

This package extends the prior region/year/New Mexico model by adding internal diagnostic factors that can help screen possible explanations for state-level variation in fatal police shooting rates. The focus is New Mexico because the earlier model showed that New Mexico remained elevated even after adjusting for population, region, and year trend.

## Important caution

Several variables in this package are **descriptive incident-composition variables** calculated from the same fatal-shooting dataset, such as gun-involved share, mental-illness-related share, and body-camera share. Those variables are useful for profiling the structure of fatal incidents, but they should **not** be interpreted as clean causal predictors. They occur inside the outcome process, so they can explain composition, not root-cause exposure.

## Data created

- `state_year_enriched_modeling_dataset.csv`: state-year modeling table with population offset, region, density, incident composition, agency-involvement proxies, and city/county concentration metrics.
- `negative_binomial_model_comparison.csv`: model-by-model comparison, including New Mexico incidence-rate ratio.
- `negative_binomial_coefficients_all_models.csv`: full coefficients and exponentiated incidence-rate ratios for every model.
- `state_residuals_after_enriched_nb_model.csv`: observed-minus-predicted state residuals from the enriched model.
- `state_factor_correlations_with_rate.csv`: simple state-level correlation screen.
- `new_mexico_factor_profile_vs_comparators.csv`: New Mexico profile versus rest of U.S. and West excluding New Mexico.

## Model sequence

The model sequence begins with the earlier region/year/New Mexico specification and then adds density, agency-involvement proxies, incident profile variables, and geographic concentration metrics.

Baseline model New Mexico IRR: **2.09**  
Baseline 95% CI: **1.65–2.63**  
Baseline p-value: **0.0000**

Selected enriched model: **M4_density_agency_profile**  
Enriched model New Mexico IRR: **1.10**  
Enriched 95% CI: **0.93–1.29**  
Enriched p-value: **0.2736**

## New Mexico profile

New Mexico's annualized fatal police shooting rate in this dataset is **10.40 per 1M residents**. Its average population density is **17.4 persons per square mile**, and **67.1%** of its fatal incidents were recorded as gun-involved. Albuquerque remains important: the top city share for New Mexico is **35.3%**.

After the enriched model, New Mexico's observed total was **219**, predicted total was **221.1**, and residual was **-2.1**.

## Main finding

The New Mexico coefficient remains elevated in the cleaner structural specifications that use region, year, population offset, density, and broad geographic concentration. However, models that include same-year agency-dispersion variables absorb most of the New Mexico signal. That is analytically interesting but not yet causal proof: `unique_agencies_with_shootings` is derived from the fatal-shooting process itself, so it behaves partly like an outcome-proximity variable. In plain English, the model is telling us that New Mexico's high rate is connected to how broadly fatal shootings are spread across agencies and places, but it is not yet telling us why that spread exists.

## Interpretation

The strongest defensible conclusion is that New Mexico's high rate likely reflects a factor stack rather than a single cause: a Western/low-density policing environment, a high share of gun-involved fatal incidents, significant Albuquerque/Bernalillo concentration, and some form of agency/geographic dispersion that the current internal dataset can detect but not fully explain. The next true external-data step should merge FBI violent crime, ACS socioeconomic variables, CDC firearm mortality, and BJS/LEMAS police staffing/policy variables.

## Recommended next model

The next publishable model should be a state-year negative-binomial or hierarchical count model using population offset and external covariates:

`fatal_shootings ~ region + year + violent_crime_rate + firearm_mortality_rate + poverty_rate + unemployment_rate + population_density + officers_per_capita + agency_count_per_capita + mental_health_provider_shortage + is_nm`

Then check whether `is_nm` remains large. If it does, the analysis should move down to county or agency level, especially Albuquerque/Bernalillo County.
