-- Year-level accuracy from transaction-level prediction tables.

DROP VIEW IF EXISTS predictions;
DROP TABLE IF EXISTS predictions;
DROP VIEW IF EXISTS filtered_predictions;
DROP VIEW IF EXISTS filtered_predictions_all;
DROP TABLE IF EXISTS filtered_predictions_national;
DROP TABLE IF EXISTS filtered_predictions_area;
DROP VIEW IF EXISTS yearly_accuracy;
DROP TABLE IF EXISTS yearly_accuracy;

CREATE OR REPLACE TABLE yearly_accuracy_national AS
SELECT
    year,
    avg(abs(price_paid - predicted_price)) AS mean_absolute_error,
    sqrt(avg((price_paid - predicted_price) * (price_paid - predicted_price))) AS rmse,
    avg(abs((price_paid - predicted_price) / price_paid)) AS mean_absolute_error_percentage,
    percentile_cont(0.25) WITHIN GROUP (
        ORDER BY abs((price_paid - predicted_price) / price_paid)
    ) AS absolute_error_percentage_q1,
    percentile_cont(0.75) WITHIN GROUP (
        ORDER BY abs((price_paid - predicted_price) / price_paid)
    ) AS absolute_error_percentage_q3,
    count(*) AS transaction_count
FROM predictions_national
GROUP BY year;

CREATE OR REPLACE TABLE yearly_accuracy_area AS
SELECT
    year,
    avg(abs(price_paid - predicted_price)) AS mean_absolute_error,
    sqrt(avg((price_paid - predicted_price) * (price_paid - predicted_price))) AS rmse,
    avg(abs((price_paid - predicted_price) / price_paid)) AS mean_absolute_error_percentage,
    percentile_cont(0.25) WITHIN GROUP (
        ORDER BY abs((price_paid - predicted_price) / price_paid)
    ) AS absolute_error_percentage_q1,
    percentile_cont(0.75) WITHIN GROUP (
        ORDER BY abs((price_paid - predicted_price) / price_paid)
    ) AS absolute_error_percentage_q3,
    count(*) AS transaction_count
FROM predictions_area
GROUP BY year;

CREATE OR REPLACE VIEW yearly_accuracy AS
SELECT * FROM yearly_accuracy_national;

CREATE OR REPLACE VIEW predictions AS
SELECT * FROM predictions_national;
