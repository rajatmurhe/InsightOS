import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
import warnings

warnings.filterwarnings('ignore')

# 1. Extract & Train Model
engine = create_engine("postgresql://rajatmurhe@localhost:5433/insightos")
df = pd.read_sql("SELECT day, SUM(sales_value) AS daily_sales FROM transactions GROUP BY day ORDER BY day;", engine)

model = IsolationForest(contamination=0.03, random_state=42)
df['anomaly_score'] = model.fit_predict(df[['daily_sales']])
anomalies = df[df['anomaly_score'] == -1].copy()

# 2. Dynamic Prompt Engineering
anomalous_data_str = anomalies.to_string(index=False)

llm_prompt = f"""
Act as a Senior Business Analyst. Review the following anomalous sales days flagged by our Machine Learning pipeline.

CONTEXT:
- The Isolation Forest model scanned {len(df)} days of historical transaction data.
- It flagged the following {len(anomalies)} days as statistically anomalous (top 3% variance).

DATA REPORT:
{anomalous_data_str}

TASK:
Write a brief, professional email to the executive team summarizing these anomalies. Please categorize them into:
1. 'Critical System Glitches' (Revenue under ₹100 - likely tracking failures)
2. 'Extreme Spikes' (Revenue over ₹20,000 - likely massive bulk orders)
3. 'Early Data Instability' (Days 1-10)
"""

# 3. Save the Engineered Prompt
with open("llm_executive_prompt.txt", "w") as file:
    file.write(llm_prompt)

print("✅ Machine Learning scan complete.")
print("✅ LLM Executive Prompt generated and saved to 'llm_executive_prompt.txt'.")