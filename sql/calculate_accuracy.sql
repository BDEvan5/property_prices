-- 1. filter predictions to those where a transaction took place in the same year
create or replace view filtered_predictions as (
    select 
        t.price_paid,
        t.deed_date,
        p.predicted_price,
        t.price_paid - p.predicted_price as error,
        (t.price_paid - p.predicted_price) / t.price_paid as error_percentage,
        t.unique_id,
        t.property_id
    from transactions_cleaned t inner join predictions p
        on t.property_id = p.property_id and year(t.deed_date) = p.year
    );

-- Export 2025 predictions to csv
COPY (
    select * from filtered_predictions where year(deed_date) = 2025
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/2025_predictions.csv' WITH CSV HEADER;
        

-- 2. Aggregate the accuracy metrics by year
CREATE OR REPLACE TABLE yearly_accuracy AS (
    SELECT
        year(deed_date) AS year,
        avg(abs(error)) AS mean_absolute_error,
        sqrt(avg(error * error)) AS rmse,
        avg(abs(error_percentage)) AS mean_error_percentage,
        count(*) AS transaction_count
    FROM filtered_predictions
    GROUP BY 1
);

-- Export yearly accuracy to csv       
COPY yearly_accuracy TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/yearly_accuracy.csv' WITH CSV HEADER;

