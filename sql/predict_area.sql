-- Outward-area PMR baseline: same pattern as national, using area_year_avg and postcode area.
-- Tables and views here are suffixed _area only (no objects shared with predict_national.sql).
-- Property PMR uses only transactions with deed_date before 2025 (holdout year for evaluation).
-- PMR steps are materialised as tables so DuckDB does not re-expand nested views (faster, lower RAM).

DROP VIEW IF EXISTS transaction_pmr_area;
DROP VIEW IF EXISTS property_pmr_area;

CREATE OR REPLACE TABLE transaction_pmr_area AS
SELECT
    t.unique_id AS transaction_id,
    t.property_id,
    t.deed_date,
    t.price_paid / a.mean_price AS price_market_ratio
FROM transactions_cleaned AS t
INNER JOIN properties AS pr ON t.property_id = pr.property_id
INNER JOIN postcodes AS pc ON pr.postcode = pc.postcode
INNER JOIN area_year_avg AS a
    ON year(t.deed_date) - 1 = a.year AND a.area = pc.area
    AND t.deed_date < DATE '2025-01-01';

-- Aggregate only from transaction_pmr_area (no second scan of transactions_cleaned).
CREATE OR REPLACE TABLE property_pmr_area AS
SELECT
    property_id,
    avg(price_market_ratio) AS mean_price_market_ratio,
    variance(price_market_ratio) AS price_market_ratio_variance,
    count(*) AS num_sales,
    min(deed_date) AS first_transaction_date,
    max(deed_date) AS last_transaction_date
FROM transaction_pmr_area
GROUP BY property_id;

CREATE OR REPLACE TABLE predictions_area AS
SELECT
    t.unique_id,
    t.property_id,
    t.deed_date,
    year(t.deed_date) AS year,
    t.price_paid,
    prev_nya.mean_price * p.mean_price_market_ratio AS predicted_price
FROM transactions_cleaned AS t
INNER JOIN properties AS pr ON t.property_id = pr.property_id
INNER JOIN postcodes AS pc ON pr.postcode = pc.postcode
INNER JOIN property_pmr_area AS p ON t.property_id = p.property_id
INNER JOIN area_year_avg AS prev_nya
    ON prev_nya.area = pc.area AND prev_nya.year = year(t.deed_date) - 1
WHERE year(t.deed_date) > year(p.first_transaction_date);

