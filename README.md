# Property Price Modeling

>**🎯 Aim:** 
> Accurately model (and predict) property transactions in the UK. For example, given a properties address and previous transactions, how accurately can I predict future transactions?

## 🧰 Code 
- `extract_transform_load.py` Extract, transform and load transaction data from HM land registry into a SQL database (using DuckDB).
- `aggregate_data.py` Aggregate the dataset to find yearly averages 
- `linear_regression.py` Linear regression model to predict average property prices in the future


## 💪 Upcoming tasks


1. **Expand the dataset:** to use all data in the price paid dataset
2. **Predict individual property transactions:** Apply the model that can predict averages to predict individual transactions, i.e. given 2 previous transactions on a property predict the next transaction price (at varying time horizons)
3. **Improve the model:** Explore more complex models to improve the predictions
4. **Automate data collection:** Deploy the database to a server and automate monthly updates (20th of the month). Make daily predictions at 1 month and 1 year ahead.
5. **Expand information sources:** Use other sources, such as interest rate, Google maps data, or news stories to improve predictions
6. **Expand the website:** Improve database analysis and display automated predictions.


#📝 Notes on the project

## 💾 Dataset

The dataset comes from the [HM land registry](https://landregistry.data.gov.uk/). 
The full dataset (~ 4.5Gb) and previous months data (~20Mb) is available for download [here](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads).


## 📝 Development notes (personal reminders)

The files are saved with `gzip` because when the page is being served on GtiHub pages, `pandas` always tries to decompress the files, which raises an error if they are not compressed. Currently, I am not sure why this is the case.
