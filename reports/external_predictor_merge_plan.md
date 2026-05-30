# External predictor merge plan

Recommended next data sources to merge by state-year:

1. ACS 5-year / Census API: poverty, unemployment, race/ethnicity, income, population density or urban/rural proxies.
2. FBI Crime Data Explorer / UCR estimates: violent crime, homicide, aggravated assault, robbery rates.
3. CDC WONDER mortality: firearm mortality, overdose mortality, suicide mortality, and other crisis-environment proxies.
4. BJS LEMAS / CSLLEA: police staffing, agency size, body-camera/policy variables where available.
5. HRSA Area Health Resources Files or provider shortage data: mental-health provider availability.

Model recommendation: negative binomial count model using fatal shootings as outcome and log(population) as an offset. Compare NM residual before and after adding external predictors.
