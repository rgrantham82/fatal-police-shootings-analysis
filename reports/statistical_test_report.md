# Police Shootings Statistical Test Report

Generated: 2026-05-17 04:05 UTC

## Data used

This report uses the cleaned per-capita package and enhanced prediction package already built in this project:

- `state_year_rates_2015_2024.csv`: 510 state-year rows, 51 jurisdictions × 10 years.
- `national_year_rates_2015_2024.csv`: 10 national annual rows.
- `clean_incidents_v2.csv`: 10,430 cleaned incident records.
- `enhanced_state_year_holdout_predictions.csv`: 102 2023-2024 state-year holdout prediction rows.

## Big-picture findings

1. **The simple national annual rate trend is upward.** OLS on national fatal-shooting rate per 1M residents estimates a slope of **+0.0503 per 1M per year** with p=0.0018. Spearman correlation also supports a monotonic upward national trend.

2. **The national unarmed fatal-shooting rate trends downward.** OLS estimates **-0.0165 unarmed fatal shootings per 1M per year**, p=0.0017. That is a meaningful descriptive pattern, though unarmed coding should be treated carefully.

3. **Once state fixed effects and population offsets are used, the annual trend is only borderline.** The state-year Poisson fixed-effects model gives an incidence rate ratio of **1.0157 per year**, p=0.0747. Translation: the national line slopes up, but the panel model is more cautious.

4. **No clean post-2020 step-change appears after state and trend adjustment.** The 2021-2024 vs. 2015-2020 incidence rate ratio is **1.0560**, p=0.3485.

5. **State geography matters strongly.** A chi-square goodness-of-fit test rejects the idea that state counts are just proportional to population exposure (p < 1e-300). The highest positive standardized residuals were **NM, AZ, CO, OK, AK**; the largest negative residuals were **NY, MA, NJ, IL, PA**.

6. **Regions differ.** Kruskal-Wallis testing across Census regions is significant, p=4.99e-06. Median annualized rates by region were: West: 5.56/1M, South: 3.99/1M, Midwest: 2.69/1M, Northeast: 1.19/1M.

7. **Body-camera indication varies by year.** The chi-square test is significant, p=1.10e-54, with Cramer's V=0.163. The yearly share ranged from **7.5%** to **30.3%**.

8. **Race/unarmed association is statistically significant but very small.** Among incidents with known race only, Cramer's V is **0.049**. This is **not** a racial per-capita risk analysis because group-specific population denominators were not included in the current package.

9. **The ensemble prediction model is not clearly biased, but residuals are non-normal.** Mean holdout error is **-1.08** fatalities, p=0.0738; Shapiro-Wilk says residuals are non-normal, p=1.23e-06.

10. **The ensemble beats weak/simple comparators, but not the strongest simple baselines.** It significantly improves over the previous-national-rate baseline and over the individual enhanced models, but not over the lag-1 or rolling-3-year baselines. The mule has spoken: the fancy model is useful, but the humble rolling average refuses to die.

## Limitations

- These are observational tests, not causal estimates.
- Per-capita denominators here are total population, not police encounters, arrests, calls for service, violent-crime exposure, or armed-encounter exposure.
- Race-specific per-capita conclusions should not be drawn from the current race table because this package has race numerator summaries but not race-specific population denominators by year and state.
- Incident-level chi-square tests can become significant with large N even when effect sizes are small.
- State-year rows have temporal and geographic dependence; the Poisson panel model used state fixed effects and cluster-robust standard errors, but that is still a simplified specification.

## Recommended next statistical upgrades

1. Add state-year violent crime rates, arrest rates, police employment, poverty/unemployment, urbanization, and firearm ownership proxy variables.
2. Build a proper negative-binomial or Bayesian hierarchical model for state-year counts with population offsets.
3. Pull ACS race-by-state-by-year denominators before making race-specific per-capita claims.
4. Add a spatial component or at least region/division random effects.
5. Use blocked or rolling-origin cross-validation for forecasting rather than only 2023-2024 holdout testing.
