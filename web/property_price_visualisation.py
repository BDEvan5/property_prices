import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    palette = sns.color_palette("Set2")
    return mo, np, palette, pd, plt


@app.cell
def _(mo):
    mo.md("""
    # Property Price Prediction

    This project aims to predict the price of a property transaction based solely on historical property data.
    """)
    return


@app.cell
def _(mo, np, pd, plt):
    _df = pd.read_csv(
        str(mo.notebook_location()) + "/public/transaction_summary.csv.gz",
        index_col=0,
        header=None,
    )

    md_element = mo.md(f"""
    - Number of transactions: {int(_df.loc["n_transactions"].item())}
    - Number of properties: {int(_df.loc["n_properties"].item())}
    - Mean price (all transactions): {_df.loc["mean_price"].item():.2f} $\pm$ {_df.loc["std_price"].item():.2f}
    """)

    _path = mo.notebook_location() / "public/price_distribution.csv.gz"
    _df_distribution = pd.read_csv(str(_path), compression="gzip")

    bin_width = _df_distribution["bin_end"] - _df_distribution["bin_start"]
    max_value = _df_distribution["bin_end"].max()
    _fig = plt.figure(figsize=(6, 3))
    plt.bar(
        _df_distribution["bin_start"],
        _df_distribution["count"],
        width=bin_width,
        align="edge",
    )
    plt.title("Distribution of Transaction Prices")
    plt.xlabel("Price Paid")
    plt.ylabel("Number of Transactions")
    xtick_marks = np.arange(0, max_value + 1, 200000)
    plt.xticks(xtick_marks, [f"{int(x / 1000)}k" for x in xtick_marks])

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    mo.vstack([mo.md("""## Database Statistics"""), mo.hstack([_fig, md_element])])
    return


@app.cell
def _(mo):
    mo.md("""
    ## House Price Index

    The raw data contains many outliers that distort the mean and standard deviation of most of the transactions. Additionally, the addition of new build houses (first time sales) skews the data.
    Therefore, the transaction data was filtered using the following steps:
    - Select transactions below the 99th percentile of the yearly average national price
    - Select properties with 2 or more transactions

    This results in the follow house-price-index (HPI) chart with corresponding volume.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    data_path = mo.notebook_location() / "public" / "avg_yearly_sales.csv.gz"
    _df = pd.read_csv(str(data_path), compression="gzip")
    hpi_data_path = mo.notebook_location() / "public" / "hpi_avg_yearly_sales.csv.gz"
    _df_hpi = pd.read_csv(str(hpi_data_path), compression="gzip")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    # Plot average price per year
    axs[0].plot(
        _df["year"],
        _df["mean_price"] / 1000,
        marker="o",
        color=palette[0],
        label="National average",
    )
    axs[0].plot(
        _df_hpi["year"],
        _df_hpi["mean_price"] / 1000,
        marker="o",
        color=palette[1],
        label="HPI",
    )
    axs[0].set_title("Average Price per Year (£1k)")
    axs[0].set_xlabel("Year")
    axs[0].grid(True)
    axs[0].spines["top"].set_visible(False)
    axs[0].spines["right"].set_visible(False)
    axs[0].legend()

    # Plot sales count per year
    axs[1].bar(
        _df["year"] - 0.2,
        _df["volume"],
        color=palette[2],
        label="National average",
        width=0.4,
    )
    axs[1].bar(
        _df_hpi["year"] + 0.2,
        _df_hpi["volume"],
        color=palette[3],
        label="HPI",
        width=0.4,
    )
    axs[1].set_title("Transactions Count per Year")
    axs[1].set_xlabel("Year")
    axs[1].grid(axis="y")
    axs[1].spines["top"].set_visible(False)
    axs[1].spines["right"].set_visible(False)
    axs[1].legend()

    plt.tight_layout()
    fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md("""
    The graph shows how the HPI is a more stable estimate of the mean price and is more useful for estimating future prices.

    The transaction count graph shos how after the 2008 crash, much fewer property transactions occurred.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Modelling

    The first approach is to build a baseline as the most simple model possible.
    This involves:
    - Calculating the proportion of the price of each property to the HPI of the previous year
        - e.g. for a house that cost 300,000 in 2011, (the HPI in 2010 is 200,000), the proportion of the HPI is 300,000 / 200,000 = 1.5
    - For each year after the first transaction, make a prediction using the previous year's HPI
        - e.g. To predict the price of the house above in 2025, multiple the factor (1.2) by the 2024 HPI of 270
    - Apply this approach to make a prediction for every property for every year.


    The accuracy of the method is measured by using the transaction data and calculating the difference between the estimated price and the actual transaction price.
    The percentage error which is calculated by dividing the absolute difference by the actual transaction price.
    The mean absolute error each year and mean absolute percentage error are plotted below.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    data_path_accuracy = mo.notebook_location() / "public" / "hpi_accuracy.csv.gz"
    hpi_accuracy = pd.read_csv(str(data_path_accuracy), compression="gzip")

    _fig, ax = plt.subplots(1, 1, figsize=(7, 3))

    ax.plot(
        hpi_accuracy["year"],
        hpi_accuracy["mean_absolute_error"],
        color=palette[0],
        linewidth=2,
    )
    ax.set_title("HPI Mean Absolute Error")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Absolute Error")
    ax.grid(axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _():
    # data_path_accuracy = mo.notebook_location() / "public" / "hpi_accuracy.csv.gz"
    # hpi_accuracy = pd.read_csv(str(data_path_accuracy), compression="gzip")

    # _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # ax1.plot(hpi_accuracy['year'], hpi_accuracy['mean_absolute_error'], color=palette[0])
    # ax1.set_title('HPI Mean Absolute Error')
    # ax1.set_xlabel('Year')
    # ax1.set_ylabel('Mean Absolute Error')
    # ax1.spines["top"].set_visible(False)
    # ax1.spines["right"].set_visible(False)

    # ax2.plot(hpi_accuracy['year'], hpi_accuracy['mean_error_percentage'], color=palette[1])
    # ax2.set_title('HPI Mean Absolute Percentage Error')
    # ax2.set_xlabel('Year')
    # ax2.set_ylabel('Mean Absolute Percentage Error')
    # ax2.spines["top"].set_visible(False)
    # ax2.spines["right"].set_visible(False)

    # plt.tight_layout()
    # plt.show()

    return


@app.cell
def _(mo):
    mo.md("""
    ## Modelling

    Since property prices have a near linear trend, the first modelling approach is to fit a linear regression (straight line) to the data.
    This line can then be extrapolated into the future to make a prediction.

    A key decision in fitting a regression, is how many years data should I use to fit the regression. The example below shows how using either 4 years or 12 years of data to fit the regression results in different predictions.
    """)
    return


@app.cell
def _(mo, pd):
    model_predictions_path = (
        mo.notebook_location() / "public" / "model_predictions.csv.gz"
    )

    df_model = pd.read_csv(str(model_predictions_path), compression="gzip")
    start_year = df_model["year"].min()
    model_periods = [
        int(col.split("_")[-1]) for col in df_model.columns if "prediction" in col
    ]
    start_error_year = start_year + max(model_periods)

    df_errors = df_model[df_model["year"] >= start_error_year]

    # Load the stats for the models
    _path = mo.notebook_location() / "public" / "linear_prediction_errors.csv.gz"
    df_stats = pd.read_csv(str(_path), compression="gzip", index_col="model_period")
    return df_errors, df_stats


@app.cell
def _(df_errors, mo, palette, pd, plt):
    model_idx_1 = 4
    model_idx_2 = 12

    plt.figure(figsize=(10, 4))
    plt.plot(
        df_errors["year"],
        df_errors["avg_price"] / 1000,
        label="Average property price",
        linewidth=2.5,
        color=palette[0],
    )

    path_1 = mo.notebook_location() / "public/linear_model_4_years.csv.gz"
    df_1 = pd.read_csv(str(path_1))
    train_df_1 = df_1[df_1["train_prediction"].notna()]
    test_df_1 = df_1[df_1["test_prediction"].notna()]
    plt.plot(
        train_df_1["year"],
        train_df_1["train_prediction"] / 1000,
        "--",
        linewidth=2,
        color=palette[1],
        label="Training Data (3 years)",
    )
    plt.plot(
        test_df_1["year"],
        test_df_1["test_prediction"] / 1000,
        "o",
        label=f"Prediction ({model_idx_1} years)",
        color=palette[1],
    )

    path_2 = mo.notebook_location() / "public/linear_model_12_years.csv.gz"
    df_2 = pd.read_csv(str(path_2))
    train_df_2 = df_2[df_2["train_prediction"].notna()]
    test_df_2 = df_2[df_2["test_prediction"].notna()]
    plt.plot(
        train_df_2["year"],
        train_df_2["train_prediction"] / 1000,
        "--",
        linewidth=2,
        color=palette[2],
        label="Training Data (12 years)",
    )
    plt.plot(
        test_df_2["year"],
        test_df_2["test_prediction"] / 1000,
        "o",
        label=f"Prediction ({model_idx_2} years)",
        color=palette[2],
    )

    plt.title("Comparing the number of years used to fit the model")
    plt.xlabel("Year")
    plt.ylabel("Price (£1k)")
    plt.legend(frameon=False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
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
    number_of_years_selector = mo.ui.slider(
        start=3, stop=12, label="Number of years to use to fit model", show_value=True
    )
    mo.md(f"""
    ### Backtesting

    Backtesting (where the model is tested on data that it has not seen before) is used to determine the best modelling approach. Linear models using 3 - 12 years of data are built and the mean absolute error is calculated for each model.

    You can view the predictions made by the different methods by selecting a number of years between 3 and 12 and then see the graph below.

    {number_of_years_selector}
    """)
    return (number_of_years_selector,)


@app.cell
def _(df_errors, df_stats, mo, number_of_years_selector, palette, plt):
    model_idx = number_of_years_selector.value

    plt.figure(figsize=(8, 3))
    plt.plot(
        df_errors["year"],
        df_errors["avg_price"] / 1000,
        label="Actual",
        linewidth=2.5,
        color=palette[0],
    )
    plt.plot(
        df_errors["year"],
        df_errors[f"prediction_{model_idx}"] / 1000,
        label=f"Prediction ({model_idx} years)",
        color=palette[1],
    )
    plt.fill_between(
        df_errors["year"],
        df_errors["avg_price"] / 1000,
        df_errors[f"prediction_{model_idx}"] / 1000,
        color="gray",
        alpha=0.2,
        label="Error region",
    )

    plt.title("Backtesting: Actual vs Predicted Average Property Prices")
    plt.xlabel("Year")
    plt.ylabel("Price (£1k)")
    plt.legend(frameon=False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.xlim(2006.5, 2025.5)
    plt.xticks(range(2007, 2027, 2))

    error_description = mo.md(f"""
    - Model horizon: {model_idx}
    - MAE: {df_stats.loc[model_idx, "MAE"]:.2f}
    - MSE: {df_stats.loc[model_idx, "MSE"]:.2f}
    """)

    mo.hstack([plt.gca(), error_description])
    return


@app.cell
def _(mo):
    mo.md("""
    The mean absolute error (MAE), which measures the average absolute difference between the predicted and actual values, is used to evaluate the performance of the models. The lower the MAE, the better the model.
    """)
    return


@app.cell
def _(df_stats, np, plt):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # MAE Plot
    _ax1.plot(df_stats.index, df_stats["MAE"])
    idx_mae = np.argmin(list(df_stats["MAE"]))
    _ax1.plot(
        df_stats.index[idx_mae], df_stats["MAE"].iloc[idx_mae], "ro", markersize=10
    )
    _ax1.set_xlabel("Number of years used in regression")
    _ax1.set_ylabel("")
    _ax1.set_title("Mean Absolute Error (MAE)")
    _ax1.spines["top"].set_visible(False)
    _ax1.spines["right"].set_visible(False)

    # MSE Plot
    _ax2.plot(df_stats.index, df_stats["MSE"])
    idx_mse = np.argmin(list(df_stats["MSE"]))
    _ax2.plot(
        df_stats.index[idx_mse], df_stats["MSE"].iloc[idx_mse], "ro", markersize=10
    )
    _ax2.set_xlabel("Number of years used in regression")
    _ax2.set_ylabel("")
    _ax2.set_title("Mean Squared Error (MSE)")
    _ax2.spines["top"].set_visible(False)
    _ax2.spines["right"].set_visible(False)

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md("""
    The graph above shows that the lowest mean absolute error (MAE) is achieved when using 6 years of data to fit the regression.

    Using this model, we can predict the average price for the upcoming year (2026).
    """)
    return


@app.cell
def _(df_errors, mo, palette, pd, plt):
    _path = mo.notebook_location() / "public/linear_model_8_years.csv.gz"
    _df = pd.read_csv(str(_path), compression="gzip")

    _train_df = _df[_df["train_prediction"].notna()]
    _test_df = _df[_df["test_prediction"].notna()]

    plt.figure(figsize=(8, 3))
    plt.plot(
        df_errors["year"],
        df_errors["avg_price"] / 1000,
        label="Average prices",
        linewidth=2.5,
        color=palette[0],
    )
    plt.plot(
        _train_df["year"],
        _train_df["train_prediction"] / 1000,
        "--",
        linewidth=2,
        color=palette[2],
        label="Training Data",
    )
    plt.plot(
        _test_df["year"],
        _test_df["test_prediction"] / 1000,
        "o",
        markersize=10,
        label="2026 Prediction",
        color=palette[3],
    )
    plt.title("Historical prices with prediction for 2026")
    plt.xlabel("Year")
    plt.ylabel("Price (£1k)")
    plt.legend()
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.xlim(2017, 2026.5)
    plt.gca()
    return


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
