CREATE OR REPLACE TABLE predictions (
    property_id UUID,
    year INT,
    predicted_price FLOAT,
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

INSERT INTO predictions (
    SELECT 
        pa.property_id,
        nya.year,
        (nya.mean_price + (pa.z_score_mean * nya.std_price)) as predicted_price
    FROM property_analysis pa
    JOIN national_year_avg nya 
        ON nya.year >= year(pa.first_transaction_date)
    ORDER BY pa.property_id, nya.year
);