-- National PMR baseline: one row per cleaned transaction with a model price.
-- PMR is from transaction_pmr_national; prediction = prior calendar year national mean × property mean PMR.
-- Property PMR uses only transactions with deed_date before 2025 (holdout year for evaluation).

CREATE OR REPLACE VIEW transaction_pmr_national AS
SELECT
    t.unique_id AS transaction_id,
    t.property_id,
    t.deed_date,
    t.price_paid / n.mean_price AS price_market_ratio
FROM transactions_cleaned AS t
INNER JOIN national_year_avg AS n ON year(t.deed_date) - 1 = n.year
WHERE n.std_price IS NOT NULL AND n.std_price > 0
    AND t.deed_date < DATE '2025-01-01';

-- Aggregate only from transaction_pmr_national (no second scan of transactions_cleaned).
CREATE OR REPLACE VIEW property_pmr_national AS
SELECT
    property_id,
    avg(price_market_ratio) AS mean_price_market_ratio,
    variance(price_market_ratio) AS price_market_ratio_variance,
    count(*) AS num_sales,
    min(deed_date) AS first_transaction_date,
    max(deed_date) AS last_transaction_date
FROM transaction_pmr_national
GROUP BY property_id;

CREATE OR REPLACE TABLE predictions_national AS
SELECT
    t.unique_id,
    t.property_id,
    t.deed_date,
    year(t.deed_date) AS year,
    t.price_paid,
    prev_nya.mean_price * p.mean_price_market_ratio AS predicted_price
FROM transactions_cleaned AS t
INNER JOIN property_pmr_national AS p ON t.property_id = p.property_id
INNER JOIN national_year_avg AS prev_nya ON prev_nya.year = year(t.deed_date) - 1
WHERE year(t.deed_date) > year(p.first_transaction_date);
