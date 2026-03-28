-- Yearly price aggregates at national, outward-area, district, sector, and full-postcode granularity.

CREATE OR REPLACE TABLE national_year_avg AS
SELECT
    year(deed_date) AS year,
    avg(price_paid) AS mean_price,
    stddev_samp(price_paid) AS std_price,
    count(*) AS volume,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY price_paid) AS q1,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY price_paid) AS median,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY price_paid) AS q3,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY price_paid) AS percentile_99,
    count(DISTINCT property_id) AS num_properties
FROM transactions_cleaned
GROUP BY year(deed_date)
ORDER BY year;

CREATE OR REPLACE TABLE area_year_avg AS
SELECT
    year(t.deed_date) AS year,
    p.area AS area,
    avg(t.price_paid) AS mean_price,
    stddev_samp(t.price_paid) AS std_price,
    count(*) AS volume
FROM transactions_cleaned AS t
INNER JOIN (
    SELECT
        properties.property_id,
        postcodes.area
    FROM properties
    INNER JOIN postcodes ON properties.postcode = postcodes.postcode
) AS p ON t.property_id = p.property_id
GROUP BY year(t.deed_date), p.area
ORDER BY year, p.area;
