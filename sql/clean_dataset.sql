

CREATE OR REPLACE VIEW properties_cleaned AS (
    select 
        property_id, 
        min(price_paid) as min_price, 
        max(price_paid) as max_price,
        count(*) as transaction_count,
        count(distinct deed_date) as unique_transaction_dates,
        count(distinct property_type) as unique_property_types,
        count(distinct estate_type) as unique_estate_types,
        count(distinct new_build) as unique_new_builds,
        count(distinct transaction_category) as unique_transaction_categories,
        any_value(transaction_category) as property_transaction_category
    from 
        transactions
    group by property_id
    having min_price > 10000 
    and max_price < 1000000  -- > 10k and < 1M
    and unique_transaction_dates = transaction_count
    and unique_property_types = 1 -- remove property type conversions
    and unique_transaction_categories = 1 -- ensure only residential transactions
    and property_transaction_category = 'A'
);

CREATE OR REPLACE VIEW transactions_cleaned AS (
    select * from transactions where property_id in (select property_id from properties_cleaned)
);

-- TODO: add data export for clean vs all transactions
--TODO: export counts of properties with each category (> 1M, <10k, transaction_category A, etc...) Show breakdown of why I clean like I do.