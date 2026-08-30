import pandas as pd
from sqlalchemy import create_engine

# Connect and query
engine = create_engine("postgresql://rajatmurhe@localhost:5433/insightos")
df = pd.read_sql("SELECT day, SUM(sales_value) AS daily_sales FROM transactions GROUP BY day ORDER BY day;", engine)

# Save to CSV
df.to_csv("data/dashboard/daily_sales.csv", index=False)
print(" Daily sales exported to CSV!")
