# Property Price Modeling

>**🎯 Aim:** 
> Accurately model (and predict) property transactions in the UK. For example, given a properties address and previous transactions, how accurately can I predict future transactions?

Demo: a current (work-in-progress) demo is available at: https://bdevan5.github.io/property_prices/

## 🧰 Code 

**SQL files for data processing:**
- `load_data.sql` Extract and load transaction data from HM land registry into a SQL database (using DuckDB).
- `transform.sql` Transform the raw data to extract property and transaction tables
- `aggregate_yearly_data.sql` Aggregate the dataset to find yearly averages for each postcode, region and district
- `house_price_index.sql` Calculate the house price index (HPI) of filtered transactions
- `hpi_predictions.sql` Make predictions for each property using the HPI
- `calculate_accuracy.sql` Calculate the accuracy of the HPI predictions


## 💪 Upcoming tasks


1. **Predict individual property transactions:** Apply the model that can predict averages to predict individual transactions, i.e. given 2 previous transactions on a property predict the next transaction price (at varying time horizons)
2. **Improve the model:** Explore more complex models to improve the predictions
3. **Automate data collection:** Deploy the database to a server and automate monthly updates (20th of the month). Make daily predictions at 1 month and 1 year ahead.
4. **Expand information sources:** Use other sources, such as interest rate, Google maps data, or news stories to improve predictions
5. **Expand the website:** Improve database analysis and display automated predictions.


# 📝 Notes on the project

## 💾 Dataset

The dataset comes from the [HM land registry](https://landregistry.data.gov.uk/). 
The full dataset (~ 4.5Gb) and previous months data (~20Mb) is available for download [here](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads).


## 📝 Development notes (personal reminders)

The files are saved with `gzip` because when the page is being served on GtiHub pages, `pandas` always tries to decompress the files, which raises an error if they are not compressed. Currently, I am not sure why this is the case.

### Compile notebotebook to HTML:

Run this command to export the notebook with outputs as an HTML page.

```bash
uv run marimo export html web/property_price_visualisation.py -o output_dir/index.html --no-include-code -f


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



**SQL planning:**
- load_data.sql
- transform.sql -> create tables
- clean_dataset.sql -> view
- aggregate_data.sql -> tables
- calculate_pmr? analyse_data? Just do a make_predictions.sql
- calculate_accuracy.sql
- export_data_to_csv - ideally, include this in each step