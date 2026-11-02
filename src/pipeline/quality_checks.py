"""Data quality checks after the load. Writes data/dashboard/dq_report.csv and returns failures.

Blocking checks fail the pipeline; warning checks are reported but do not stop it.
"""
import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DASH_DIR, DB_URI

CHECKS = [
    ("blocking", "null keys in transactions",
     "SELECT COUNT(*) FROM transactions WHERE household_key IS NULL OR basket_id IS NULL OR product_id IS NULL OR day IS NULL"),
    ("blocking", "duplicate product_id in products",
     "SELECT COUNT(*) FROM (SELECT product_id FROM products GROUP BY product_id HAVING COUNT(*) > 1) d"),
    ("blocking", "transactions with no matching product",
     "SELECT COUNT(*) FROM transactions t LEFT JOIN products p ON p.product_id = t.product_id WHERE p.product_id IS NULL"),
    ("warning", "negative sales_value rows",
     "SELECT COUNT(*) FROM transactions WHERE sales_value < 0"),
    ("warning", "rows with quantity over 100 (likely fuel or misc, excluded from unit KPIs)",
     "SELECT COUNT(*) FROM transactions WHERE quantity > 100"),
    ("warning", "days with no transactions inside the date range",
     "SELECT (MAX(day) - MIN(day) + 1) - COUNT(DISTINCT day) FROM transactions"),
]


def main(db_uri: str = DB_URI) -> int:
    engine = create_engine(db_uri)
    rows = []
    with engine.connect() as conn:
        for level, name, sql in CHECKS:
            bad = int(conn.execute(text(sql)).scalar() or 0)
            status = "PASS" if bad == 0 else ("FAIL" if level == "blocking" else "WARN")
            rows.append({"check": name, "level": level, "bad_rows": bad, "status": status})
            print(f"[{status}] {name}: {bad}")
        top = pd.read_sql(text(
            "SELECT p.department, COUNT(*) AS rows_over_100 FROM transactions t JOIN products p "
            "ON p.product_id = t.product_id WHERE t.quantity > 100 GROUP BY p.department "
            "ORDER BY rows_over_100 DESC LIMIT 5"), conn)
    if len(top):
        print("Departments with quantity over 100:\n" + top.to_string(index=False))
    os.makedirs(DASH_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(DASH_DIR, "dq_report.csv"), index=False)
    return sum(r["status"] == "FAIL" for r in rows)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
