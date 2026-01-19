create or replace view hpi_transaction_predictions as (
    select 
        t.price_paid,
        t.deed_date,
        p.predicted_price,
        t.price_paid - p.predicted_price as error,
        (t.price_paid - p.predicted_price) / t.price_paid as error_percentage,
        t.unique_id,
        t.property_id
    from transactions t inner join hpi_predictions p
        on t.property_id = p.property_id and year(t.deed_date) = p.year
    );
        
CREATE OR REPLACE TABLE hpi_accuracy AS (
    SELECT
        year(deed_date) AS year,
        avg(abs(error)) AS mean_absolute_error,
        sqrt(avg(error * error)) AS rmse,
        avg(abs(error_percentage)) AS mean_error_percentage,
        count(*) AS transaction_count
    FROM hpi_transaction_predictions
    WHERE price_paid < 1000000 and price_paid > 10000
    GROUP BY 1
);

        