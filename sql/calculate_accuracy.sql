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
    select deed_date, predicted_price, price_paid, error, error_percentage from filtered_predictions where year(deed_date) = 2025
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/2025_predictions.csv' WITH CSV HEADER;
        

-- 2. Aggregate the accuracy metrics by year
CREATE OR REPLACE TABLE yearly_accuracy AS (
    SELECT
        year(deed_date) AS year,
        avg(abs(error)) AS mean_absolute_error,
        sqrt(avg(error * error)) AS rmse,
        avg(abs(error_percentage)) AS mean_absolute_error_percentage,
        percentile_cont(0.25) within group (order by abs(error_percentage)) AS absolute_error_percentage_q1,
        percentile_cont(0.75) within group (order by abs(error_percentage)) AS absolute_error_percentage_q3,
        count(*) AS transaction_count
    FROM filtered_predictions
    GROUP BY 1
);

-- Export yearly accuracy to csv       
COPY yearly_accuracy TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/yearly_accuracy.csv' WITH CSV HEADER;


-- 3. Examples (best and worst predictions)

COPY (
    with example_properties as (
        select property_id, count(*) as transactions_count from transactions_cleaned 
        group by property_id  
        having transactions_count > 5 and max(year(deed_date)) = 2025
    ), best_properties as (
        select p.property_id from filtered_predictions p 
        where year(p.deed_date) = 2025 
            and p.property_id in (select property_id from example_properties) 
        order by abs(p.error_percentage) asc limit 1 -- asc gets the smallest error
    )
    select 
        p.year, p.predicted_price, t.price_paid 
    from predictions p left join transactions_cleaned t 
        on p.property_id = t.property_id and p.year = year(t.deed_date)
    where p.property_id in (select property_id from best_properties)
    order by p.year
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/example_prediction_best.csv' WITH CSV HEADER;


COPY (
    with example_properties as (
        select property_id, count(*) as transactions_count from transactions_cleaned 
        group by property_id  
        having transactions_count > 5 and max(year(deed_date)) = 2025
    ), worst_properties as (
        select p.property_id from filtered_predictions p 
        where year(p.deed_date) = 2025 and 
            p.property_id in (select property_id from example_properties) 
        order by abs(p.error_percentage) desc limit 1 -- desc gets the biggest error
    )
    select 
        p.year, p.predicted_price, t.price_paid 
    from predictions p left join transactions_cleaned t 
        on p.property_id = t.property_id and p.year = year(t.deed_date)
    where p.property_id in (select property_id from worst_properties)
    order by p.year
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/example_prediction_worst.csv' WITH CSV HEADER;
