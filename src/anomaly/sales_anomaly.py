import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
import warnings

warnings.filterwarnings('ignore')

# 1. Connect to PostgreSQL
DB_URI = "postgresql://rajatmurhe@localhost:5433/insightos"
engine = create_engine(DB_URI)

print("Fetching daily sales data from PostgreSQL...")

# 2. Extract Daily Sales via SQL
query = """
SELECT 
    day, 
    SUM(sales_value) AS daily_sales 
FROM transactions 
GROUP BY day 
ORDER BY day;
"""
df = pd.read_sql(query, engine)

print(f"Loaded {len(df)} days of transaction history.")
print("Training AI Anomaly Detector (Isolation Forest)...")

# 3. Train the ML Model (Flagging the top 3% most unusual days)
model = IsolationForest(contamination=0.03, random_state=42)
df['anomaly_score'] = model.fit_predict(df[['daily_sales']])

# 4. Filter and Display Anomalies
anomalies = df[df['anomaly_score'] == -1].copy()

print("\n⚠️ SYSTEM ALERT: Unusual Sales Activity Detected ⚠️")
print("======================================================")

for index, row in anomalies.iterrows():
    day = int(row['day'])
    sales = row['daily_sales']
    print(f"Day {day:03d} | Revenue: ₹{sales:,.2f} (Statistically Anomalous)")
    
print("\n✅ AI scan complete. Ready for business investigation.")