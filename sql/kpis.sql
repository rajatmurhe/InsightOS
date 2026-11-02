-- Executive KPIs built from CTEs. Unit based KPIs exclude departments whose quantity is not an
-- item count (fuel, misc transactions). The department list comes from NON_UNIT_DEPARTMENTS in src/config.py.
WITH line_items AS (
    SELECT t.basket_id, t.household_key, t.quantity, t.sales_value,
           CASE WHEN p.department IN :non_unit_departments THEN 0 ELSE 1 END AS counts_as_units
    FROM transactions t
    LEFT JOIN products p ON p.product_id = t.product_id
),
baskets AS (
    SELECT basket_id,
           SUM(sales_value) AS basket_value,
           SUM(CASE WHEN counts_as_units = 1 THEN quantity ELSE 0 END) AS basket_units
    FROM line_items
    GROUP BY basket_id
)
SELECT
    ROUND(CAST((SELECT SUM(sales_value) FROM line_items) AS NUMERIC), 2)                 AS total_sales,
    (SELECT SUM(quantity) FROM line_items WHERE counts_as_units = 1)                     AS total_units_sold,
    (SELECT COUNT(*) FROM baskets)                                                       AS total_baskets,
    (SELECT COUNT(DISTINCT household_key) FROM line_items)                               AS unique_households,
    ROUND(CAST((SELECT AVG(basket_value) FROM baskets) AS NUMERIC), 2)                   AS average_basket_value,
    ROUND(CAST((SELECT AVG(basket_units) FROM baskets) AS NUMERIC), 2)                   AS average_units_per_basket
