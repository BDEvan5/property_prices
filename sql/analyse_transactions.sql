CREATE OR REPLACE TABLE transactions_analysis (
    z_score FLOAT,
    transaction_id UUID,
    FOREIGN KEY (transaction_id) REFERENCES transactions(unique_id)
);

INSERT INTO transactions_analysis (transaction_id, z_score) (
    select t.unique_id, (t.price_paid - n.mean_price) / n.std_price as z_score
    from transactions t JOIN national_year_avg n
        ON year(t.deed_date) = n.year
);



