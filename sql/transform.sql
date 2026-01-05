
CREATE OR REPLACE VIEW properties_view AS (
    select "paon", "saon", "street", "locality", "town", "district", "county", "postcode", uuid() 
    AS "property_id" from raw_data group by all
);

CREATE OR REPLACE VIEW transactions_view AS (
    SELECT unique_id AS transaction_id, price_paid, deed_date, property_type, estate_type, new_build, transaction_category,  property_id FROM raw_data NATURAL JOIN properties_view;
);