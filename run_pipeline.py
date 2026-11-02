"""Run the whole InsightOS pipeline: load, quality checks, exports, anomaly detection, alert."""
import sys

from src.anomaly import llm_alert, sales_anomaly
from src.pipeline import export_dashboard, load_raw, quality_checks


def main() -> int:
    load_raw.main()
    if quality_checks.main():
        print("Blocking data quality check failed: stopping before exports.")
        return 1
    export_dashboard.main()
    sales_anomaly.main()
    llm_alert.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
