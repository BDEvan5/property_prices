
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
FROM raw_data r 
LEFT JOIN properties p 
    ON r.paon IS NOT DISTINCT FROM p.paon
    AND r.saon IS NOT DISTINCT FROM p.saon
    AND r.street IS NOT DISTINCT FROM p.street
    AND r.locality IS NOT DISTINCT FROM p.locality
    AND r.town IS NOT DISTINCT FROM p.town
    AND r.district IS NOT DISTINCT FROM p.district
    AND r.county IS NOT DISTINCT FROM p.county
    AND r.postcode IS NOT DISTINCT FROM p.postcode;


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