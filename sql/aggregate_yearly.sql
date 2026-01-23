


CREATE OR REPLACE TABLE national_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price_paid) AS q1,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY price_paid) AS median,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price_paid) AS q3,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY price_paid) AS percentile_99,
        COUNT(DISTINCT property_id) as num_properties
    FROM transactions_cleaned
    GROUP BY year
    ORDER BY year
);

COPY national_year_avg TO '/Users/b.evans/Documents/ml_development/property_prices/web/public/national_year_avg.csv' WITH CSV HEADER;

CREATE OR REPLACE TABLE area_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        p.area as area
    FROM 
        transactions_cleaned t JOIN (
            properties JOIN postcodes 
            ON properties.postcode = postcodes.postcode
        ) 
        p on t.property_id = p.property_id
    GROUP BY year, p.area
    ORDER BY year, p.area
);

CREATE OR REPLACE TABLE district_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        p.area_district as area
    FROM 
        transactions_cleaned t JOIN (
            properties JOIN postcodes 
            ON properties.postcode = postcodes.postcode
        ) 
        p on t.property_id = p.property_id
    GROUP BY year, p.area_district
    ORDER BY year, p.area_district
);

CREATE OR REPLACE TABLE sector_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        p.area_district_sector as area
    FROM 
        transactions_cleaned t JOIN (
            properties JOIN postcodes 
            ON properties.postcode = postcodes.postcode
        ) 
        p on t.property_id = p.property_id
    GROUP BY year, p.area_district_sector
    ORDER BY year, p.area_district_sector
);

CREATE OR REPLACE TABLE postcode_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        p.postcode  as  postcode
    FROM transactions_cleaned t JOIN properties p on t.property_id = p.property_id
    GROUP BY year, p.postcode
    ORDER BY year, p.postcode
);
