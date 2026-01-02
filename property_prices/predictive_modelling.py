import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    from sklearn.linear_model import LinearRegression
    import numpy as np

    import matplotlib.pyplot as plt
    import duckdb
    import pandas as pd

    import os
    if os.getcwd().endswith("property_prices/property_prices"):
        os.chdir("..")
    return LinearRegression, duckdb, np, plt


@app.cell
def _(duckdb):

    con = duckdb.connect("data/main.db")
    df = con.sql("""SELECT * FROM year_avg_data""").df()

    START_YEAR = df["year"].min()
    END_YEAR = df["year"].max()
    print(START_YEAR, END_YEAR)

    model_periods = list(range(3, 13))


    return END_YEAR, START_YEAR, df, model_periods


@app.cell
def _(END_YEAR, LinearRegression, START_YEAR, df, model_periods):
    # loop through model periods and make predictions
    for model_period in model_periods:
        num_updates = END_YEAR - START_YEAR - model_period
        for i in range(num_updates + 1): # add 1 for the final prediction
            start, end = START_YEAR + i, START_YEAR + i + model_period
            update_data = df[(df["year"] >= start) & (df["year"] < end)]
            model_i = LinearRegression()
            model_i.fit(update_data[["year"]].values, update_data[["avg_price"]].values)

            prediction = model_i.predict([[end]])
            df.loc[i + model_period, f"prediction_{model_period}"] = prediction

    df.to_csv("web/public/model_predictions.csv", index=False)
    return


@app.cell
def _(START_YEAR, df, model_periods, np, plt):
    start_error_year = START_YEAR + model_periods[-1]
    df_error = df[df["year"] >= start_error_year]
    mean_absolute_errors = {
        model_period: (df_error[f"prediction_{model_period}"] - df_error["avg_price"]).abs().mean().item() 
        for model_period in model_periods
    }
    plt.plot(mean_absolute_errors.keys(), mean_absolute_errors.values())
    idx = np.argmin(list(mean_absolute_errors.values()))
    plt.plot(model_periods[idx], list(mean_absolute_errors.values())[idx], 'ro', markersize=10)
    plt.xlabel('Number of years used in regression')
    plt.ylabel('Mean Absolute Error (MAE)')
    plt.title('Error vs period used in regression')
    plt.show()
    return (start_error_year,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df, plt, start_error_year):

    plt.figure(figsize=(12, 6))
    df_plot = df[df["year"] >= start_error_year]
    for model_idx in [3, 6, 12]:
        plt.plot(df_plot["year"], df_plot[f"prediction_{model_idx}"]/1000, label=f"Prediction ({model_idx} years)")
    plt.plot(df_plot["year"], df_plot["avg_price"] / 1000, label="Actual", linewidth=4)
    plt.title('Actual vs Predicted Average Property Prices')
    plt.xlabel('Year')
    plt.ylabel('Price (£1k)')
    plt.legend()
    plt.show()
    return


@app.cell
def _(df, plt):
    plt.figure(figsize=(12, 6))
    plt.plot(df["year"], df["avg_price"], label="Actual")
    plt.plot(df["year"], df["prediction_6"], label="Prediction (1 year)")
    plt.title('Actual vs Predicted Average Property Prices')
    plt.xlabel('Observations')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

    return


if __name__ == "__main__":
    app.run()
