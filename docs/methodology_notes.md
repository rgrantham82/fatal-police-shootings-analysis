# Methodology Notes

## Count modeling

Fatal police shootings are count data. Poisson models are a natural first attempt, but state-year counts show overdispersion, meaning variance exceeds the mean. Negative binomial models are therefore a better choice for inference.

## Offset terms

For state-year rate modeling, population should be included as an exposure offset:

```text
offset = log(population)
```

This lets the model estimate rate differences rather than simply rewarding larger states for being large.

## Incidence rate ratios

Negative binomial coefficients are in log-rate units. Exponentiating coefficients gives incidence rate ratios.

Example:

```text
coefficient = 0.7349
exp(0.7349) = 2.09
```

This means the modeled rate is approximately 2.09 times the comparison group rate, holding other included variables constant.

## New Mexico model interpretation

The New Mexico indicator remained significant after region and year adjustment. That suggests New Mexico is not merely high because it is Western or because of broad national time trends.

## Causality caution

The models in this project are exploratory. They identify associations and residual patterns. Causal claims require stronger designs, cleaner external predictors, and more complete contact denominators.
