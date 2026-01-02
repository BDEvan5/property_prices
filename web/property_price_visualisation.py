import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    import numpy as np
    import marimo as mo

    import matplotlib.pyplot as plt
    import duckdb
    import pandas as pd

    import seaborn as sns

    palette = sns.color_palette("Set2")
    return mo, np, palette, pd, plt


@app.cell
def _():
    import os
    if os.getcwd().endswith("web"):
        os.chdir("..")

    print(os.getcwd())
    return


@app.cell
def _(mo):
    mo.md("""
    # Property Price Visualisation

    This introductory project analyses historical property price transaction data fro the TA11 post code region, and uses it to predict future pricing trends.
    """)
    return


@app.cell
def _(mo, pd):
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/transaction_summary.csv", index_col=0)


    mo.md(f"""
    ## Database Statistics

     - Number of transactions: {int(_df.loc['count'].item())}
     - Mean price (all transactions): {_df.loc['mean'].item():.2f} $\pm$ {_df.loc['std'].item():.2f}
     - Median price: {_df.loc['50%'].item():.2f}
     - Price range (cheapest to most expensive): {int(_df.loc['min'].item())} to {int(_df.loc['max'].item())}
    """)
    return


@app.cell
def _(mo, pd):
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/transaction_summary.csv")
    _df

    return


@app.cell
def _(mo):
    mo.md("""
    ### Yearly aggregated data

    I aggregated the data by year to understand the trends in the market.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    data_path = mo.notebook_location() / "public" / "avg_yearly_sales.csv.gz"
    print(str(data_path))
    _df = pd.read_csv(str(data_path), compression="gzip")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    # Plot average price per year
    axs[0].plot(_df["year"], _df["avg_price"] / 1000, marker="o", color=palette[0])
    axs[0].set_title("Average Price per Year (£1k)")
    axs[0].set_xlabel("Year")
    axs[0].grid(True)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)

    # Plot sales count per year
    axs[1].bar(_df["year"], _df["sales_count"], color=palette[1])
    axs[1].set_title("Transactions Count per Year")
    axs[1].set_xlabel("Year")
    axs[1].grid(axis="y")
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)

    plt.tight_layout()
    fig 
    return


@app.cell
def _(mo):
    mo.md("""
    The graph above shows that the average price increases consistently year over year. Two exceptional periods that characterise the graph are:
    1. The years following the global financial crisis (2009-2012): prices didn't increase as much as they did in the years before and sales volumes were lower
    2. The COVID-19 pandemic (2020-2021): the low interest rates causes the prices to increase more dramatically than previous years.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Modelling

    Since property prices have a near linear trend, the first modelling approach is to fit a linear regression (straight line) to the data.
    This line can then be extrapolated into the future to make a prediction.

    A key decision in fitting a regression, is how many years data should I use to fit the regression. The example below shows how using either 3 years or 12 years of data to fit the regression results in different predictions.
    """)
    return


@app.cell
def _(LinearRegression, mo, palette, pd, plt, start_error_year):
    model_idx_1 = 3
    model_idx_2 = 12
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/model_predictions.csv")

    plt.figure(figsize=(10, 4))
    _df = _df[_df["year"] >= start_error_year]
    plt.plot(_df["year"], _df["avg_price"] / 1000, label="Average property price", linewidth=2.5, color=palette[0])

    model_1 = LinearRegression()
    train_start_year_1 = 2025 - model_idx_1
    df_1 = _df[_df["year"] >= train_start_year_1]
    train_years_1 = df_1["year"].values.reshape(-1, 1)
    model_1.fit(train_years_1, df_1["avg_price"])
    train_predictions_1 = model_1.predict(train_years_1)
    prediction_2026_1 = model_1.predict([[2026]])

    model_2 = LinearRegression()
    train_start_year_2 = 2025 - model_idx_2
    df_2 = _df[_df["year"] >= train_start_year_2]
    train_years_2 = df_2["year"].values.reshape(-1, 1)
    model_2.fit(train_years_2, df_2["avg_price"])
    train_predictions_2 = model_2.predict(train_years_2)
    prediction_2026_2 = model_2.predict([[2026]])

    plt.plot(train_years_1, train_predictions_1/1000, '--', linewidth=2, color=palette[1], label="Training Data (3 years)")
    plt.plot(2026, prediction_2026_1/1000, 'o', label=f"Prediction ({model_idx_1} years)", color=palette[1])
    plt.plot(train_years_2, train_predictions_2/1000, '--', linewidth=2, color=palette[2], label="Training Data (12 years)")
    plt.plot(2026, prediction_2026_2/1000, 'o', label=f"Prediction ({model_idx_2} years)", color=palette[2])
    plt.title('Comparing the number of years used to fit the model')
    plt.xlabel('Year')
    plt.ylabel('Price (£1k)')
    plt.legend(frameon=False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlim(2012, 2026.5)

    plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""
    The plot shows that using a different numbers of years as training data has a bit impact on the model. Now lets calculate the ideal number of years to use to fit the model.
    """)
    return


@app.cell
def _(mo):

    number_of_years_selector = mo.ui.number(start=3, stop=12)
    mo.md(f"""
    ### Backtesting

    I used back testing to compare using varying numbers of years.
    Back testing is where you use historical data to test your modelling approach.

    You can view the predictions made by the different methods by selecting a number of years between 3 and 12 and then see the graph below.
    Number of years used to fit the model: {number_of_years_selector}
    """)
    return (number_of_years_selector,)


@app.cell
def _(mo, number_of_years_selector, palette, pd, plt, start_error_year):
    model_idx = number_of_years_selector.value
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/model_predictions.csv")

    plt.figure(figsize=(8, 3))
    _df = _df[_df["year"] >= start_error_year]
    plt.plot(_df["year"], _df["avg_price"] / 1000, label="Actual", linewidth=2.5, color=palette[0])
    plt.plot(_df["year"], _df[f"prediction_{model_idx}"]/1000, label=f"Prediction ({model_idx} years)", color=palette[1])
    plt.fill_between(_df["year"], _df["avg_price"] / 1000, _df[f"prediction_{model_idx}"]/1000, color='gray', alpha=0.2, label="Error region")

    plt.title('Backtesting: Actual vs Predicted Average Property Prices')
    plt.xlabel('Year')
    plt.ylabel('Price (£1k)')
    plt.legend(frameon=False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlim(2006.5, 2025.5)
    plt.xticks(range(2007, 2027, 2))
    plt.gca()
    return


@app.cell
def _(mo):
    mo.md("""
    The mean absolute error (MAE), which measures the average absolute difference between the predicted and actual values, is used to evaluate the performance of the models. The lower the MAE, the better the model.
    """)
    return


@app.cell
def _(mo, np, pd, plt):
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/model_predictions.csv")

    start_year = _df["year"].min()
    model_periods = [int(col.split("_")[-1]) for col in _df.columns if "prediction" in col]
    start_error_year = start_year + max(model_periods)
    _df = _df[_df["year"] >= start_error_year]
    mean_absolute_errors = {
        model_period: (_df[f"prediction_{model_period}"] - _df["avg_price"]).abs().mean().item() 
        for model_period in model_periods
    }

    plt.figure(figsize=(8, 4))
    plt.plot(mean_absolute_errors.keys(), mean_absolute_errors.values())
    idx = np.argmin(list(mean_absolute_errors.values()))
    plt.plot(model_periods[idx], list(mean_absolute_errors.values())[idx], 'ro', markersize=10)
    plt.xlabel('Number of years used in regression')
    plt.ylabel('Mean Absolute Error (MAE)')
    plt.title('Error vs period used in regression')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca()
    return (start_error_year,)


@app.cell
def _(mo):
    mo.md("""
    The graph above shows that the lowest mean absolute error (MAE) is achieved when using 6 years of data to fit the regression.

    Using this model, we can predict the average price for the upcoming year (2026).
    """)
    return


@app.cell
def _(mo, palette, pd, plt, start_error_year):
    from sklearn.linear_model import LinearRegression
    selected_model_idx = 6
    _df = pd.read_csv(str(mo.notebook_location()) + "/public/model_predictions.csv")

    model = LinearRegression()
    train_start_year = 2025 - selected_model_idx
    df_fit = _df[_df["year"] >= train_start_year]
    train_years = df_fit["year"].values.reshape(-1, 1)
    model.fit(train_years, df_fit["avg_price"])
    train_predictions = model.predict(train_years)
    prediction_2026 = model.predict([[2026]])

    plt.figure(figsize=(8, 3))
    _df = _df[_df["year"] >= start_error_year]
    plt.plot(_df["year"], _df["avg_price"] / 1000, label="Average prices", linewidth=2.5, color=palette[0])
    # plt.plot(_df["year"], _df[f"prediction_{selected_model_idx}"]/1000, label=f"Prediction ({selected_model_idx} years)", color=palette[1])
    plt.plot(train_years, train_predictions/1000, '--', linewidth=2, color=palette[2], label="Training Data")
    plt.plot([2026], [prediction_2026/1000], 'o', markersize=10, label="2026 Prediction", color=palette[3])
    plt.title('Historical prices with prediction for 2026')
    plt.xlabel('Year')
    plt.ylabel('Price (£1k)')
    plt.legend()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlim(2018, 2026.5)
    plt.gca()
    return LinearRegression, prediction_2026


@app.cell
def _(mo, prediction_2026):
    mo.md(f"""
    The exact prediction for the average property price in 2026 is **£{prediction_2026[0]:.2f}**.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Conclusion

    This v0.1 project analyses a dataset of property transactions in the TA11 area to understand historical trends and build a basic model to predict future prices. Backtesting was used to select the number of years to use to train the model and a final prediction for the average property price in 2026 was calculated.

    Future versions of the project plan to:
    - Increase the data set to all of England
    - Use a more complex model to predict prices
    - Automate dataset expansion, model prediction & accuracy tracking
    - Take other information into account, such as the interest rate
    """)
    return


if __name__ == "__main__":
    app.run()
