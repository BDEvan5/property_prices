
CREATE OR REPLACE TABLE properties AS (
    select paon, saon, street, locality, town, district, county, postcode, uuid() 
    AS property_id from raw_data group by all
);

CREATE OR REPLACE VIEW transactions_view AS (
    SELECT unique_id AS transaction_id, price_paid, deed_date, property_type, estate_type, new_build, transaction_category, property_id FROM raw_data NATURAL JOIN properties
);

CREATE OR REPLACE TABLE postcodes AS (
    SELECT 
        postcode,
        -- 1. Area: Leading letters only
        REGEXP_EXTRACT(postcode, '^([A-Z]+)', 1) AS area,
        
        -- 2. District: Everything before the space
        REGEXP_EXTRACT(postcode, '^([^ ]+)', 1) AS area_district,
        
        -- 3. Sector: Everything before the space, plus the space and the first digit
        REGEXP_EXTRACT(postcode, '^([^ ]+ [0-9])', 1) AS area_district_sector,
    FROM properties 
    GROUP BY ALL
);