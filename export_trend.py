"""Kept for backward compatibility: exports the dashboard CSVs. Prefer `python run_pipeline.py`."""
from src.pipeline import export_dashboard

if __name__ == "__main__":
    export_dashboard.main()
