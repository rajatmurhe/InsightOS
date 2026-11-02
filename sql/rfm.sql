-- RFM segmentation in SQL. Each household gets 1 to 5 on Recency, Frequency and Monetary
-- (5 = best) using NTILE, then a segment from those scores.
WITH last_day AS (
    SELECT MAX(day) AS max_day FROM transactions
),
household AS (
    SELECT household_key,
           (SELECT max_day FROM last_day) - MAX(day) AS recency_days,
           COUNT(DISTINCT basket_id)                  AS frequency_baskets,
           ROUND(CAST(SUM(sales_value) AS NUMERIC), 2) AS total_spend
    FROM transactions
    GROUP BY household_key
),
scored AS (
    SELECT household_key, recency_days, frequency_baskets, total_spend,
           NTILE(5) OVER (ORDER BY recency_days DESC)    AS r_score,
           NTILE(5) OVER (ORDER BY frequency_baskets ASC) AS f_score,
           NTILE(5) OVER (ORDER BY total_spend ASC)       AS m_score
    FROM household
)
SELECT household_key, recency_days, frequency_baskets, total_spend, r_score, f_score, m_score,
       CASE
           WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '1 - Champions'
           WHEN f_score >= 4 AND m_score >= 3                  THEN '2 - Loyal Customers'
           WHEN r_score >= 4 AND f_score <= 2                  THEN '3 - New or Promising'
           WHEN r_score <= 2 AND f_score >= 3                  THEN '4 - At Risk'
           ELSE                                                     '5 - Hibernating'
       END AS rfm_segment
FROM scored
ORDER BY total_spend DESC
