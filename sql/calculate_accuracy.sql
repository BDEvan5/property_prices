CREATE OR REPLACE VIEW hpi_cleaned_properties AS (
    select 
        property_id, 
        min(price_paid) as min_price, 
        max(price_paid) as max_price,
        count(*) as transaction_count,
        count(distinct deed_date) as unique_transaction_dates,
        count(distinct property_type) as unique_property_types,
        count(distinct estate_type) as unique_estate_types,
        count(distinct new_build) as unique_new_builds,
        count(distinct transaction_category) as unique_transaction_categories,
        any_value(transaction_category) as property_transaction_category
    from 
        transactions
    group by property_id
    having min_price > 10000 and max_price < 1000000 
    and unique_transaction_dates = transaction_count
    and unique_property_types = 1
    and unique_estate_types = 1
    and unique_new_builds = 1
    and unique_transaction_categories = 1
    and property_transaction_category = 'A'
);



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
    where t.property_id in (select property_id from hpi_cleaned_properties)
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

        
COPY hpi_accuracy TO '/Users/b.evans/Documents/ml_development/property_prices/hpi_accuracy.csv' WITH CSV HEADER;

