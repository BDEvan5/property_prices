-- 1. Calculate price-market-ratio (PMR) of each transaction

-- Use the previous year's average price for each transaction
-- The PMR = price_paid / previous_year_average_price
CREATE OR REPLACE VIEW transaction_pmr AS (
    select 
        t.unique_id as transaction_id, 
        (t.price_paid - n.mean_price) / n.std_price AS z_score,
        t.price_paid / n.mean_price AS price_market_ratio
    from transactions t JOIN national_year_avg n
        ON year(t.deed_date) - 1 = n.year
);


-- 2. Aggregate per-property PMR
CREATE OR REPLACE VIEW property_pmr AS (
    select 
        t.property_id, 
        AVG(a.z_score) as z_score_mean, 
        variance(a.z_score) as z_score_variance, 
        AVG(a.price_market_ratio) as mean_price_market_ratio,
        variance(a.price_market_ratio) as price_market_ratio_variance,
        COUNT(*) as num_sales,
        MIN(t.deed_date) as first_transaction_date,
        MAX(t.deed_date) as last_transaction_date
    from transaction_pmr a JOIN transactions t ON a.transaction_id = t.unique_id
    GROUP BY t.property_id
);


-- 3. Make predictions for each property for every year after purchase
CREATE OR REPLACE TABLE predictions (
    property_id UUID,
    year INT,
    predicted_price FLOAT,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

INSERT INTO predictions (
    SELECT 
        p.property_id,
        nya.year,
        prev_nya.mean_price * p.mean_price_market_ratio as predicted_price
    FROM property_pmr p
    JOIN national_year_avg nya 
        ON nya.year > year(p.first_transaction_date)
    JOIN national_year_avg prev_nya
        ON prev_nya.year = nya.year - 1
    ORDER BY p.property_id, nya.year
);

-- 4. Export data

-- TODO: export example with >8 transactions with the PMR per-transaction and for the property and the predicted prices for each year after purchase.


COPY (
    with example_properties as (
        select property_id, count(*) as transactions_count from transactions_cleaned group by property_id  having transactions_count > 5 order by transactions_count desc
    )
    select 
        p.year, p.predicted_price, t.price_paid 
    from predictions p left join transactions_cleaned t on p.property_id = t.property_id and p.year = year(t.deed_date)
    where p.property_id in (select property_id from example_properties limit 1)
    order by p.year
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/example_prediction.csv' WITH CSV HEADER;



COPY (
    with example_properties as (
        select property_id, count(*) as transactions_count from transactions_cleaned group by property_id  having transactions_count > 5 order by transactions_count desc
    )
    select 
        p.year, p.predicted_price, t.price_paid 
    from predictions p left join transactions_cleaned t on p.property_id = t.property_id and p.year = year(t.deed_date)
    where p.property_id in (select property_id from example_properties limit 1 offset 1)
    order by p.year
) TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/example_prediction_worst.csv' WITH CSV HEADER;

