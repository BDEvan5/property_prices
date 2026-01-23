# Property Price Modeling

>**🎯 Aim:** 
> Accurately model (and predict) property transactions in the UK. For example, given a properties address and previous transactions, how accurately can I predict future transactions?

Demo: a current demo is available at: https://bdevan5.github.io/property_prices/

## 🧰 Code 

**SQL files for data processing:**
- `load_data.sql`: Extract and load transaction data from HM land registry into a SQL database (using DuckDB).
- `transform.sql`: Transform the raw data to extract property and transaction tables and create a postcode view.
- `clean_dataset.sql`: Filter transactions to remove anomalies and ensure data quality.
- `aggregate_yearly.sql`: Aggregate the dataset to find yearly averages for each postcode, region, district, and nationally.
- `make_predictions.sql`: Calculate z-scores for properties and generate price predictions based on national averages.
- `calculate_accuracy.sql`: Calculate the accuracy of the predictions against actual transaction data.
- `export_data_to_csv.sql`: Export various metrics and datasets to CSV for the web visualization.


## 💪 Upcoming tasks

1. **Improve prediction model:**
    - Estimate the confidence of the prediction, i.e. what error is due to property variance (irreducible) vs model bias (reducible)
    - Use the location (postcode) of each property
    - Use a rolling average rather than fixed yearly average
    - Consider weighting later price-market-ratios as more accurate than older ones
    - Increase frequency of estimates to monthly
2. **Deployment:**
    - Deploy database as DuckLake 
    - Automate database expansion (new data published on the 20th of each month)
    - Automate monthly estimates and accuracy measurements
3. **Website:**
    - Build interactive website that estimates the real-value of each property (depends on a deployed database)
    - Show visualisation for each property with historical transactions & geographically similar properties


# 📝 Notes on the project

## 💾 Dataset

The dataset comes from the [HM land registry](https://landregistry.data.gov.uk/). 
The full dataset (~ 4.5Gb) and previous months data (~20Mb) is available for download [here](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads).


## 📝 Development notes (personal reminders)

### Compile notebotebook to HTML:

Run this command to export the notebook with outputs as an HTML page.

```bash
uv run marimo export html web/property_price_visualisation.py -o web/output/index.html --no-include-code -f
```

### Data notes
- `property_type`: 
    - Detached
    - Semi-detached
    - Terraced
    - Flat
    - Other
- `estate_type`: 
    - L = Leasehold
    - C = Freehold
- `new_build`: 
    - Y = New build
    - N = Not a new build
- `transaction_category`: 
    - A = residential
    - B = commercial transaction


## SQL with DuckDB

Current pipeline has two steps:
1. Open a DuckDB instance and experiment with the command that you want to run
2. Write and run and `.sql` file

These `.sql` files can be run using the following commands:
```bash
duckdb -f sql/load_data.sql data/properties.db
```