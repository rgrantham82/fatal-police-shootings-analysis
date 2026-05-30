"""Create core portfolio visuals from processed data."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path("data/processed")
FIGS = Path("figures/generated")
FIGS.mkdir(parents=True, exist_ok=True)


def main() -> None:
    national = pd.read_csv(DATA / "national_year_rates_2015_2024.csv")

    plt.figure(figsize=(10, 6))
    plt.plot(national["year"], national["fatal_shootings"], marker="o")
    plt.title("National Fatal Police Shootings by Year")
    plt.xlabel("Year")
    plt.ylabel("Fatal shootings")
    plt.tight_layout()
    plt.savefig(FIGS / "national_fatal_shootings_trend.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(national["year"], national["fatal_shooting_rate_per_1m"], marker="o")
    plt.title("National Fatal Police Shooting Rate per 1M Residents")
    plt.xlabel("Year")
    plt.ylabel("Rate per 1M")
    plt.tight_layout()
    plt.savefig(FIGS / "national_rate_per_1m_trend.png", dpi=180)
    plt.close()

    print(f"Wrote figures to {FIGS}")


if __name__ == "__main__":
    main()
