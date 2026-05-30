"""Albuquerque-focused analysis template.

This script summarizes Albuquerque incident records if the processed ABQ files
are present.
"""
from pathlib import Path
import pandas as pd

DATA = Path("data/processed")


def main() -> None:
    detail_path = DATA / "abq_albuquerque_incident_detail_2015_2024.csv"
    if not detail_path.exists():
        raise FileNotFoundError("Missing Albuquerque detail file. Run the ABQ extraction step first.")

    df = pd.read_csv(detail_path)
    print("Albuquerque records:", len(df))

    for col in ["armed_with", "threat_type", "flee_status", "race_label"]:
        if col in df.columns:
            print(f"\n{col}\n", df[col].value_counts(dropna=False).head(10))


if __name__ == "__main__":
    main()
