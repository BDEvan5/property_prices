CREATE OR REPLACE TABLE transactions_analysis (
    transaction_id UUID,
    z_score FLOAT,
    proportion_of_mean FLOAT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(unique_id)
);

INSERT INTO transactions_analysis (transaction_id, z_score, proportion_of_mean) (
    select 
        t.unique_id, 
        (t.price_paid - n.mean_price) / n.std_price AS z_score,
        t.price_paid / n.mean_price AS proportion_of_mean
    from transactions t JOIN national_year_avg n
        ON year(t.deed_date) = n.year
);



