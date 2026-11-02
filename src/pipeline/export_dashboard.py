"""Run the analytics SQL and export the CSVs that feed the Tableau dashboard."""
import os

import pandas as pd
from sqlalchemy import bindparam, create_engine, text

from src.config import DASH_DIR, DB_URI, NON_UNIT_DEPARTMENTS, read_sql


def main(db_uri: str = DB_URI) -> dict:
    engine = create_engine(db_uri)
    os.makedirs(DASH_DIR, exist_ok=True)
    kpi_sql = text(read_sql("kpis.sql")).bindparams(bindparam("non_unit_departments", expanding=True))
    with engine.connect() as conn:
        outputs = {
            "kpis_executive.csv": pd.read_sql(kpi_sql, conn, params={"non_unit_departments": list(NON_UNIT_DEPARTMENTS)}),
            "daily_sales.csv": pd.read_sql(text(read_sql("daily_sales.sql")), conn),
            "customer_rfm.csv": pd.read_sql(text(read_sql("rfm.sql")), conn),
        }
    for name, df in outputs.items():
        df.to_csv(os.path.join(DASH_DIR, name), index=False)
        print(f"Exported {name} ({len(df):,} rows)")
    return outputs


if __name__ == "__main__":
    main()
