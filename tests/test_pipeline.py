"""End to end test on a small SYNTHETIC sample shaped like The Complete Journey (SQLite)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.anomaly import llm_alert, sales_anomaly  # noqa: E402
from src.pipeline import export_dashboard, load_raw, quality_checks  # noqa: E402


def make_sample(raw_dir):
    rng = np.random.default_rng(0)
    products = pd.DataFrame({
        "PRODUCT_ID": [1, 2, 3, 4],
        "MANUFACTURER": [10, 11, 12, 13],
        "DEPARTMENT": ["GROCERY", "PRODUCE", "KIOSK-GAS", "DRUG GM"],
        "BRAND": ["National", "Private", "National", "National"],
        "COMMODITY_DESC": ["SOUP", "FRUIT", "GASOLINE", "VITAMINS"],
        "SUB_COMMODITY_DESC": ["A", "B", "C", "D"],
        "CURR_SIZE_OF_PRODUCT": ["10 OZ", "1 LB", "", "60 CT"],
    })
    rows = []
    basket = 1000
    for day in range(1, 201):
        n_baskets = 30 if day != 150 else 300        # day 150 is a planted spike
        for _ in range(n_baskets):
            basket += 1
            hh = int(rng.integers(1, 51))
            for pid in rng.choice([1, 2, 3, 4], size=2, replace=False):
                qty = int(rng.integers(5000, 20000)) if pid == 3 else int(rng.integers(1, 4))
                rows.append([hh, basket, day, int(pid), qty, round(float(rng.uniform(1, 20)), 2),
                             1, 0.0, 1200, day // 7 + 1, 0.0, 0.0])
    tx = pd.DataFrame(rows, columns=[c.upper() for c in load_raw.TRANSACTION_COLS])
    os.makedirs(raw_dir, exist_ok=True)
    products.to_csv(os.path.join(raw_dir, "product.csv"), index=False)
    tx.to_csv(os.path.join(raw_dir, "transaction_data.csv"), index=False)
    return tx


@pytest.fixture
def env(tmp_path, monkeypatch):
    raw, dash, rep = tmp_path / "raw", tmp_path / "dash", tmp_path / "reports"
    monkeypatch.setattr(load_raw, "RAW_DIR", str(raw))
    for mod in (quality_checks, export_dashboard, sales_anomaly, llm_alert):
        monkeypatch.setattr(mod, "DASH_DIR", str(dash))
    monkeypatch.setattr(llm_alert, "REPORT_DIR", str(rep))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    tx = make_sample(str(raw))
    return os.environ.get("TEST_DB_URI", f"sqlite:///{tmp_path / 'test.db'}"), tx, dash, rep


def test_full_pipeline(env):
    db, tx, dash, rep = env
    counts = load_raw.main(db)
    assert counts["transactions"] == len(tx)
    assert load_raw.main(db)["transactions"] == len(tx)        # rerun does not duplicate rows
    assert quality_checks.main(db) == 0

    out = export_dashboard.main(db)
    kpi = out["kpis_executive.csv"].iloc[0]
    non_fuel_units = tx.loc[tx["PRODUCT_ID"] != 3, "QUANTITY"].sum()
    assert kpi["total_units_sold"] == non_fuel_units            # fuel quantity excluded
    assert kpi["average_units_per_basket"] < 10
    assert kpi["total_baskets"] == tx["BASKET_ID"].nunique()
    rfm = out["customer_rfm.csv"]
    assert rfm["household_key"].is_unique and rfm[["r_score", "f_score", "m_score"]].isin(range(1, 6)).all().all()

    anomalies = sales_anomaly.main()
    assert 150 in set(anomalies["day"])                         # the planted spike is caught
    assert anomalies["day"].min() >= 100                        # warm up days are skipped
    llm_alert.main()
    assert (rep / "llm_executive_prompt.txt").exists()
