-- Filter properties and transactions for modelling (residential, plausible prices, no duplicate same-day sales).

CREATE OR REPLACE VIEW properties_cleaned AS
SELECT
    property_id,
    min(price_paid) AS min_price,
    max(price_paid) AS max_price,
    count(*) AS transaction_count,
    count(DISTINCT deed_date) AS unique_transaction_dates,
    count(DISTINCT property_type) AS unique_property_types,
    count(DISTINCT estate_type) AS unique_estate_types,
    count(DISTINCT new_build) AS unique_new_builds,
    count(DISTINCT transaction_category) AS unique_transaction_categories,
    any_value(transaction_category) AS property_transaction_category
FROM transactions
GROUP BY property_id
HAVING min_price > 10000
    AND max_price < 1000000
    AND unique_transaction_dates = transaction_count
    AND unique_property_types = 1
    AND unique_transaction_categories = 1
    AND property_transaction_category = 'A';

CREATE OR REPLACE VIEW transactions_cleaned AS
SELECT *
FROM transactions
WHERE property_id IN (SELECT property_id FROM properties_cleaned);
