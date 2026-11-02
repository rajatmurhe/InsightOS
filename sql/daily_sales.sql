-- Total sales value per day.
SELECT day, ROUND(CAST(SUM(sales_value) AS NUMERIC), 2) AS daily_sales
FROM transactions
GROUP BY day
ORDER BY day
