"""Run statistical tests for the fatal police shootings project.

This script is a portfolio-friendly template. It expects processed files in
`data/processed/` and writes outputs to `data/processed/`.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

DATA = Path("data/processed")


def main() -> None:
    national = pd.read_csv(DATA / "national_year_rates_2015_2024.csv")
    state_rates = pd.read_csv(DATA / "state_overall_rates_2015_2024.csv")

    results = []

    # National trend test
    x = national["year"].to_numpy()
    y = national["fatal_shooting_rate_per_1m"].to_numpy()
    slope, intercept, r, p, se = stats.linregress(x, y)
    results.append(
        {
            "test": "national_linear_rate_trend",
            "statistic": slope,
            "p_value": p,
            "interpretation": "Estimated annual change in fatal shooting rate per 1M residents.",
        }
    )

    # Region test if region exists
    if (
        "region" in state_rates.columns
        and "annualized_rate_per_1m" in state_rates.columns
    ):
        groups = [
            g["annualized_rate_per_1m"].dropna().to_numpy()
            for _, g in state_rates.groupby("region")
        ]
        h, p = stats.kruskal(*groups)
        results.append(
            {
                "test": "kruskal_region_rate_difference",
                "statistic": h,
                "p_value": p,
                "interpretation": "Tests whether state rates differ across Census regions.",
            }
        )

    out = pd.DataFrame(results)
    out.to_csv(DATA / "portfolio_statistical_tests.csv", index=False)
    print(out)


if __name__ == "__main__":
    main()
