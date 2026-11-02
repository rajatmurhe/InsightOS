"""Shared settings. The database URL comes from the environment, never from the code."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_URI = os.environ.get("INSIGHTOS_DB_URI", "postgresql+psycopg://localhost:5432/insightos")
RAW_DIR = os.path.join(ROOT, "data", "raw")
DASH_DIR = os.path.join(ROOT, "data", "dashboard")
SQL_DIR = os.path.join(ROOT, "sql")
REPORT_DIR = os.path.join(ROOT, "reports")

# Departments whose QUANTITY is not a count of items (fuel and misc transactions).
# They are kept for revenue, but excluded from unit based KPIs. Check dq_report.csv after a load.
NON_UNIT_DEPARTMENTS = ("KIOSK-GAS", "MISC SALES TRAN", "MISC. TRANS.", "COUP/STR & MFG")


def read_sql(name: str) -> str:
    with open(os.path.join(SQL_DIR, name)) as f:
        return f.read()
