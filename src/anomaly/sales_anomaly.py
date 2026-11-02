"""Flag unusual sales days with an Isolation Forest.

Features: daily sales and its ratio to the median of the 7 days before it, so a day is judged
against its own recent level. The first WARMUP_DAYS days are skipped: in The Complete Journey the
household panel ramps up (median daily sales climb from about 1.8k to 10k over the first ~100 days),
which would otherwise be flagged as anomalies. Writes data/dashboard/anomalies.csv.
"""
import os

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.config import DASH_DIR

CONTAMINATION = 0.03
WARMUP_DAYS = 100
FEATURES = ["daily_sales", "ratio_to_trailing"]


def detect(daily: pd.DataFrame, contamination: float = CONTAMINATION) -> pd.DataFrame:
    df = daily.sort_values("day").reset_index(drop=True).copy()
    df["daily_sales"] = df["daily_sales"].astype(float)
    df["trailing_median"] = df["daily_sales"].shift(1).rolling(7, min_periods=3).median()
    df["ratio_to_trailing"] = df["daily_sales"] / df["trailing_median"]
    scored = df[df["day"] > df["day"].min() + WARMUP_DAYS - 1].dropna(subset=["ratio_to_trailing"]).copy()
    model = IsolationForest(contamination=contamination, random_state=42)
    scored["is_anomaly"] = model.fit_predict(scored[FEATURES]) == -1
    scored["anomaly_score"] = model.score_samples(scored[FEATURES])
    return scored[scored["is_anomaly"]][["day", "daily_sales", "trailing_median", "ratio_to_trailing", "anomaly_score"]]


def main() -> pd.DataFrame:
    daily = pd.read_csv(os.path.join(DASH_DIR, "daily_sales.csv"))
    anomalies = detect(daily)
    anomalies.round(3).to_csv(os.path.join(DASH_DIR, "anomalies.csv"), index=False)
    print(f"Scanned {len(daily)} days, flagged {len(anomalies)} as anomalous:")
    print(anomalies.round(2).to_string(index=False))
    return anomalies


if __name__ == "__main__":
    main()
