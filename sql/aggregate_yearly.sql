-- Should this be a table or a view?
CREATE OR REPLACE TABLE national_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume
    FROM transactions_view
    GROUP BY year
    ORDER BY year
);

CREATE OR REPLACE TABLE area_year_avg AS (
    SELECT 
        year(deed_date) as year,
        AVG(price_paid) as mean_price,
        STDDEV_SAMP(price_paid) as std_price,
        COUNT(*) as volume,
        p.area as area
    FROM 
        transactions_view t JOIN (
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
        transactions_view t JOIN (
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
        transactions_view t JOIN (
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
    FROM transactions_view t JOIN properties p on t.property_id = p.property_id
    GROUP BY year, p.postcode
    ORDER BY year, p.postcode
);
