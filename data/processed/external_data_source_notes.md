# External Data Source Notes for Next Integration

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
