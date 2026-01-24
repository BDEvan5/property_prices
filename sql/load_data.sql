CREATE OR REPLACE TABLE raw_data AS (
        SELECT * FROM read_csv(
        'data/raw_land_registry/transactions_Dec25.csv', 
        header=false, 
        columns={'unique_id': 'uuid', 'price_paid': 'INTEGER', 'deed_date': 'DATE', 'postcode': 'VARCHAR', 'property_type': 'VARCHAR', 'new_build': 'VARCHAR', 'estate_type': 'VARCHAR', 'saon': 'VARCHAR', 'paon': 'VARCHAR', 'street': 'VARCHAR', 'locality': 'VARCHAR', 'town': 'VARCHAR', 'district': 'VARCHAR', 'county': 'VARCHAR', 'transaction_category': 'VARCHAR', 'linked_data_uri': 'VARCHAR'})
);
-- Alternatively, replace the file path with a URL to the raw data file
-- http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv