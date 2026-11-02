"""Turn the flagged anomalies into an executive alert.

Always writes the engineered prompt to reports/llm_executive_prompt.txt. If OPENAI_API_KEY is set,
it also sends the prompt to an OpenAI compatible chat API (set OPENAI_BASE_URL for providers such as
Groq, and LLM_MODEL for the model name) and saves the reply to reports/executive_alert.md.
"""
import os

import pandas as pd
import requests

from src.config import DASH_DIR, REPORT_DIR


def build_prompt(anomalies: pd.DataFrame, days_scanned: int) -> str:
    return f"""Act as a senior business analyst. Review the sales days flagged by our anomaly model.

CONTEXT:
- An Isolation Forest scanned {days_scanned} days of transactions (after a 100 day warm up while the panel ramps up).
- It flagged {len(anomalies)} days. ratio_to_trailing compares each day with the median of the 7 days before it.

DATA:
{anomalies.round(2).to_string(index=False)}

TASK:
Write a short email to the executive team. Group the days into likely data or tracking problems
(sales far below normal) and genuine demand spikes (sales far above normal), say which to investigate
first, and keep it under 200 words."""


def call_llm(prompt: str) -> str:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={"model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
              "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main() -> str:
    anomalies = pd.read_csv(os.path.join(DASH_DIR, "anomalies.csv"))
    days = len(pd.read_csv(os.path.join(DASH_DIR, "daily_sales.csv")))
    prompt = build_prompt(anomalies, days)
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(os.path.join(REPORT_DIR, "llm_executive_prompt.txt"), "w") as f:
        f.write(prompt)
    print("Prompt saved to reports/llm_executive_prompt.txt")
    if os.environ.get("OPENAI_API_KEY"):
        alert = call_llm(prompt)
        with open(os.path.join(REPORT_DIR, "executive_alert.md"), "w") as f:
            f.write(alert)
        print("Executive alert saved to reports/executive_alert.md")
        return alert
    print("OPENAI_API_KEY not set: skipped the LLM call (prompt only).")
    return prompt


if __name__ == "__main__":
    main()
