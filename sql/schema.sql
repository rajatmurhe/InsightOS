-- InsightOS warehouse tables (PostgreSQL). Source: dunnhumby "The Complete Journey".
-- Grain of transactions: one product line within one basket.
CREATE TABLE IF NOT EXISTS products (
    product_id           BIGINT PRIMARY KEY,
    manufacturer         INTEGER,
    department           VARCHAR(40),
    brand                VARCHAR(20),
    commodity_desc       VARCHAR(60),
    sub_commodity_desc   VARCHAR(60),
    curr_size_of_product VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS transactions (
    household_key     INTEGER NOT NULL,
    basket_id         BIGINT NOT NULL,
    day               INTEGER NOT NULL,
    product_id        BIGINT NOT NULL,
    quantity          INTEGER NOT NULL,
    sales_value       NUMERIC(10, 2) NOT NULL,
    store_id          INTEGER,
    retail_disc       NUMERIC(10, 2),
    trans_time        INTEGER,
    week_no           INTEGER,
    coupon_disc       NUMERIC(10, 2),
    coupon_match_disc NUMERIC(10, 2)
);

CREATE INDEX IF NOT EXISTS idx_transactions_day ON transactions (day);
CREATE INDEX IF NOT EXISTS idx_transactions_household ON transactions (household_key);
