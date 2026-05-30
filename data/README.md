# Data Notes

This repository contains processed analytical outputs and summary datasets generated during the project. It does not attempt to replace the original source datasets.

## Primary source

The main incident source is the Washington Post Fatal Force dataset:

https://github.com/washingtonpost/data-police-shootings

## Population denominators

State-year rates use U.S. Census population estimates. Albuquerque first-pass rates used Census QuickFacts city population estimates.

## Recommended external merges

Future explanatory modeling should merge:

- ACS poverty, unemployment, race/ethnicity, age, and housing indicators;
- FBI Crime Data Explorer violent-crime rates;
- CDC WONDER firearm mortality and overdose mortality rates;
- BJS LEMAS police staffing, training, equipment, and policy indicators;
- APD calls for service, arrests, officer staffing, use-of-force reports, and officer-involved shooting records.

## Important denominator caution

Resident population is useful for public-rate comparisons, but it is not a true exposure denominator for police shootings. Better denominators include calls for service, arrests, violent-crime incidents, weapons calls, and officer staffing.
