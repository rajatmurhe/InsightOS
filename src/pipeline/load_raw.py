"""Load the raw dunnhumby CSVs (data/raw/) into the warehouse.

Expects data/raw/transaction_data.csv and data/raw/product.csv from "The Complete Journey"
(download from dunnhumby's source files page; the CSVs are not committed to this repo).
Each run truncates and reloads the tables, so reruns give the same result.
"""
import os

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DB_URI, RAW_DIR, read_sql

TRANSACTION_COLS = ["household_key", "basket_id", "day", "product_id", "quantity", "sales_value",
                    "store_id", "retail_disc", "trans_time", "week_no", "coupon_disc", "coupon_match_disc"]
PRODUCT_COLS = ["product_id", "manufacturer", "department", "brand", "commodity_desc",
                "sub_commodity_desc", "curr_size_of_product"]
CHUNK = 100_000


def read_raw(name: str, cols: list) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(RAW_DIR, name))
    df.columns = [c.strip().lower() for c in df.columns]
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {sorted(missing)}")
    return df[cols]


def main(db_uri: str = DB_URI) -> dict:
    engine = create_engine(db_uri)
    with engine.begin() as conn:
        for stmt in read_sql("schema.sql").split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        conn.execute(text("DELETE FROM transactions"))
        conn.execute(text("DELETE FROM products"))

    products = read_raw("product.csv", PRODUCT_COLS).drop_duplicates("product_id")
    transactions = read_raw("transaction_data.csv", TRANSACTION_COLS)
    products.to_sql("products", engine, if_exists="append", index=False, chunksize=CHUNK)
    transactions.to_sql("transactions", engine, if_exists="append", index=False, chunksize=CHUNK)
    counts = {"products": len(products), "transactions": len(transactions)}
    print(f"Loaded {counts['products']:,} products and {counts['transactions']:,} transaction lines")
    return counts


if __name__ == "__main__":
    main()
