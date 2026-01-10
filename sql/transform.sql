
CREATE OR REPLACE TABLE properties (
    property_id UUID PRIMARY KEY,
    paon VARCHAR,
    saon VARCHAR,
    street VARCHAR,
    locality VARCHAR,
    town VARCHAR,
    district VARCHAR,
    county VARCHAR,
    postcode VARCHAR
);

INSERT INTO properties 
SELECT 
    uuid() AS property_id,
    paon, saon, street, locality, town, district, county, postcode
FROM raw_data 
GROUP BY ALL;

-- CREATE OR REPLACE TABLE properties AS ( 
--     select paon, saon, street, locality, town, district, county, postcode, uuid() 
--     AS property_id from raw_data group by all
-- );

CREATE OR REPLACE TABLE transactions (
    unique_id UUID PRIMARY KEY,
    price_paid INTEGER,
    deed_date DATE,
    property_type VARCHAR,
    estate_type VARCHAR,
    new_build VARCHAR,
    transaction_category VARCHAR,
    property_id UUID,
    -- Define the Foreign Key constraint here
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
);

-- Populate transactions table
INSERT INTO transactions 
SELECT 
    r.unique_id, 
    r.price_paid, 
    r.deed_date, 
    r.property_type, 
    r.estate_type, 
    r.new_build, 
    r.transaction_category,
    p.property_id
FROM raw_data r NATURAL JOIN properties p;

-- CREATE OR REPLACE VIEW transactions_view AS (
--     SELECT unique_id AS transaction_id, price_paid, deed_date, property_type, estate_type, new_build, transaction_category, property_id FROM raw_data NATURAL JOIN properties
-- );

CREATE OR REPLACE VIEW postcodes AS ( 
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