"""New Mexico focused count-model template.

Uses negative binomial regression with a population offset where suitable columns exist.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA = Path("data/processed")


def main() -> None:
    df = pd.read_csv(DATA / "state_year_rates_2015_2024.csv")
    df["is_nm"] = (df["state"] == "NM").astype(int)
    df["year_centered"] = df["year"] - df["year"].mean()

    formula = "fatal_shootings ~ C(region) + is_nm + year_centered"
    model = smf.negativebinomial(
        formula=formula,
        data=df,
        offset=np.log(df["population"])
    ).fit(disp=False)

    print(model.summary())
    irr = np.exp(model.params)
    print("\nIncidence rate ratios:\n", irr)


if __name__ == "__main__":
    main()
