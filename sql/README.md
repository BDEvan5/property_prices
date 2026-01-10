# SQL pipeline

Current pipeline has two steps:
1. Open a DuckDB instance and experiment with the command that you want to run
2. Write and run and `.sql` file



These `.sql` files can be run using the following commands:
```bash
duckdb -f sql/load_data.sql data/properties.db
```

More generally, duckdb uses:

```bash
duckdb -f file_name.sql database_name.db
```

## Directory:

- `load_data.sql`: Load raw data into a DuckDB database. You can select to download directly, or load from a local `.csv` file.
- `transform.sql`: Transform the raw data into a properties table and a transactions table. Additionally, the postcodes are stored in a view with the area, district, and sector extracted for easy future use.
- `aggregate_yearly.sql`: Aggregate the data yearly by area, district, sector, and postcode.
- `analyse_transactions.sql`: Calculate the z-score for each transaction.
- `analyse_properties.sql`: Calculate the mean z-score and the variance of the z-scores for each property.
- `make_predictions.sql`: Make predictions for each property using the z-score and the national yearly average.



