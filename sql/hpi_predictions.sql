-- NOTES:
-- Use all properties and all transactions with averages from HPI



CREATE OR REPLACE VIEW hpi_transaction_analysis AS (
    select 
        t.unique_id as transaction_id, 
        (t.price_paid - n.mean_price) / n.std_price AS z_score,
        t.price_paid / n.mean_price AS proportion_of_mean
    from transactions t JOIN hpi_national_year_avg n
        ON year(t.deed_date) = n.year
);


CREATE OR REPLACE VIEW hpi_property_analysis AS (
    select 
        t.property_id, 
        AVG(a.z_score) as z_score_mean, 
        variance(a.z_score) as z_score_variance, 
        AVG(a.proportion_of_mean) as mean_proportion_mean,
        variance(a.proportion_of_mean) as mean_proportion_variance,
        COUNT(*) as num_sales,
        MIN(t.deed_date) as first_transaction_date,
        MAX(t.deed_date) as last_transaction_date
    from hpi_transaction_analysis a JOIN transactions t ON a.transaction_id = t.unique_id
    GROUP BY t.property_id
);

CREATE OR REPLACE TABLE hpi_predictions (
    property_id UUID,
    year INT,
    predicted_price FLOAT,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

INSERT INTO hpi_predictions (
    SELECT 
        pa.property_id,
        nya.year,
        nya.mean_price * pa.mean_proportion_mean as predicted_price
        -- (nya.mean_price + (pa.z_score_mean * nya.std_price)) as predicted_price
    FROM hpi_property_analysis pa
    JOIN hpi_national_year_avg nya 
        ON nya.year >= year(pa.first_transaction_date)
    ORDER BY pa.property_id, nya.year
);