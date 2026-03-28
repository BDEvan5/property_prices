-- Land Registry CSV as a view (no duplicate storage; each scan reads the file).
-- Run from the repository root so paths resolve. Adjust the CSV path to your file.

CREATE OR REPLACE VIEW raw_data AS
SELECT *
FROM read_csv(
    'data/raw_land_registry/transactions_Dec25.csv',
    header = false,
    columns = {
        'unique_id': 'uuid',
        'price_paid': 'INTEGER',
        'deed_date': 'DATE',
        'postcode': 'VARCHAR',
        'property_type': 'VARCHAR',
        'new_build': 'VARCHAR',
        'estate_type': 'VARCHAR',
        'saon': 'VARCHAR',
        'paon': 'VARCHAR',
        'street': 'VARCHAR',
        'locality': 'VARCHAR',
        'town': 'VARCHAR',
        'district': 'VARCHAR',
        'county': 'VARCHAR',
        'transaction_category': 'VARCHAR',
        'linked_data_uri': 'VARCHAR'
    }
);
