CREATE OR REPLACE TABLE property_analysis (
    z_score_mean FLOAT,
    z_score_variance FLOAT,
    mean_proportion_mean FLOAT,
    mean_proportion_variance FLOAT,
    num_sales INTEGER,
    first_transaction_date DATE,
    last_transaction_date DATE,
    property_id UUID,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

INSERT INTO property_analysis (property_id, z_score_mean, z_score_variance, mean_proportion_mean, mean_proportion_variance, num_sales, first_transaction_date, last_transaction_date) (
    select 
        t.property_id, 
        AVG(a.z_score) as z_score_mean, 
        variance(a.z_score) as z_score_variance, 
        AVG(a.proportion_of_mean) as mean_proportion_mean,
        variance(a.proportion_of_mean) as mean_proportion_variance,
        COUNT(*) as num_sales,
        MIN(t.deed_date) as first_transaction_date,
        MAX(t.deed_date) as last_transaction_date
    from transactions_analysis a JOIN transactions t ON a.transaction_id = t.unique_id
    GROUP BY t.property_id
);



