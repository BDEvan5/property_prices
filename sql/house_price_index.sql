CREATE OR REPLACE VIEW transactions_99th_percentile AS (
    select 
        t.*,
    FROM transactions t JOIN national_year_avg n
        ON year(t.deed_date) = n.year
    WHERE t.price_paid < n.percentile_99
);

-- select properties that have >1 transaction in transactions_99th_percentile
CREATE OR REPLACE VIEW hpi_properties AS (
    select 
        property_id,
        COUNT(*) as num_transactions,
        AVG(price_paid) as avg_price_paid,
        MIN(price_paid) as min_price_paid,
        MAX(price_paid) as max_price_paid,
        MIN(deed_date) as first_transaction_date,
        MAX(deed_date) as last_transaction_date
    FROM transactions_99th_percentile 
    group by property_id having count(*) > 1
);


-- aggregate transactions from hpi_properties
CREATE OR REPLACE VIEW hpi_transactions AS (
    SELECT *
    FROM transactions_99th_percentile
    WHERE property_id IN (SELECT property_id FROM hpi_properties)
);


-- aggregate hpi_transactions
CREATE OR REPLACE TABLE hpi_national_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        COUNT(DISTINCT property_id) as num_properties,
        MAX(price_paid) as max_price_paid
    FROM hpi_transactions
    GROUP BY year
    ORDER BY year
);


