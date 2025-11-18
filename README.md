# property_prices
Modeling property prices in the UK


# Project Notes

## Overview

The development pipeline for all three of the required sections will be the same. Start out by getting them to run locally on my laptop and then later on move them to a server where they run in real time.

### Data handling (probably this repo)
- Collect the data (and updates) from HM land registry
- Preprocess the data and store in the database (.vortex files)
- Process data into outputs that will be displayed on the website, i.e. avg price per year

**Future automation:**
Automatically run update jobs to collect new data daily.

### Website
Static website that displays data stored in the git repo.
- Show historical price data & volume of house sold
- Specifically show plots where the same property has sold later and record that increase

**Future automation:**
- Upgrade to a full website that queries the database for real-time info
NOTE: unless the data is changing frequently, it might be more worth while to just run a job to update the website data each night and then I can sick with a static website.

### Modelling repo

This will start as an offline system, that could be moved online later on.
The role will be to use the processed data from the data handling to make predictions that are stored as part of the website data to be displayed.

**Future automation:**

Run daily updated predictions 

## MVP

- Add the TA11 database and export data required for the website
- Make a website showing plots:
    - Price trend & volume over time
    - Houses that have sold multiple times 
    - Busiest months for house sales
- Make a simple model (think linear regression) that makes a prediction for 1 month from now
- Add the prediction to the website with a model description

## Notes

I need two tables to ingest the data:
- Property table that records each unique property with address information
- Transactions table that records the transactions for each property

NOTE: in the future, I also need a method to handle property changes, i.e. plot to house

