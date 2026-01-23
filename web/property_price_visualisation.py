import marimo

__generated_with = "0.19.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from scipy.stats import gaussian_kde

    palette = plt.get_cmap("Set2").colors
    return gaussian_kde, mo, np, palette, pd, plt


@app.cell
def _(mo):
    mo.md("""
    # Property Price Prediction

    This project uses property data from the [HM Land Registry](https://landregistry.data.gov.uk/) to estimate the value of property transactions.
    Since 1995, the Land Registry has been recording the price of every property transaction in the UK.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Database Statistics (raw data)
    The raw data is loaded into a SQL database (DuckDB) and transformed to have properties and transactions tables.
    """)
    return


@app.cell
def _(mo, np, palette, pd, plt):
    _df = pd.read_csv(
        str(mo.notebook_location()) + "/public/transaction_summary.csv",
        index_col=0,
        header=None,
    )

    md_element = mo.md(f"""
    - Number of transactions: {int(_df.loc["n_transactions"].item()):,}
    - Number of properties: {int(_df.loc["n_properties"].item()):,}
    - Mean price (all transactions): £{_df.loc["mean_price"].item():,.2f} $\pm$ {_df.loc["std_price"].item():,.2f}
    """)

    _path = mo.notebook_location() / "public/price_distribution.csv"
    _df_distribution = pd.read_csv(str(_path))

    _fig = plt.figure(figsize=(6, 3))
    plt.bar(
        _df_distribution["bin_end"],
        _df_distribution["count"],
        width=_df_distribution["bin_end"].iloc[0],
        align="edge",
        color=palette[1],
    )
    plt.title("Distribution of Transaction Prices")
    plt.xlabel("Price Paid")
    plt.ylabel("Number of Transactions")
    xtick_marks = np.arange(0, _df_distribution["bin_end"].max() + 1, 200000)
    plt.xticks(xtick_marks, [f"{int(x / 1000)}k" for x in xtick_marks])

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    mo.hstack([_fig, md_element])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### The 2025 Prediction challenge

    > **Challenge:**
    >
    > Predict the transaction value for each property that was sold in 2025, using all the data until the end of 2024.

    The raw data above is cleaned for training and prediction by applying the following filters:
    - Prices below £1M and above £10k
    - Remove type 'B' commercial transactions
    - Houses with constant property types
    - Remove houses with multiple transactions on the same day
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _df = pd.read_csv(
        str(mo.notebook_location()) + "/public/transactions_cleaned_by_year.csv",
        header=0,
    )

    # Create standalone plot
    _fig, _ax = plt.subplots(figsize=(8, 3))

    _ax.bar(
        _df["transaction_year"] - 0.2,
        _df["count_all"],
        color=palette[3],
        label="All transactions",
        width=0.4,
    )
    _ax.bar(
        _df["transaction_year"] + 0.2,
        _df["count_cleaned"],
        color=palette[2],
        label="Cleaned transactions",
        width=0.4,
    )

    _ax.set_title("Num Transactions per Year")
    _ax.set_xlabel("Year")
    _ax.grid(axis="y")
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend()

    plt.tight_layout()
    plt.show()
    return


@app.cell
def _():
    # TODO: consider adding a pie chart showing how many transactions each filter excluded
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Modelling Approach

    In predicting the price of a property, I assume that the value of a property relative to the property market remains constant. While it is a simplification, it is neccessary since no data on the style, kind or condition of the house is availble.

    The modelling approach has three steps:
    1. Calculate the yearly average property price
    2. Estimate the value of each property relative to the previous year's average
    3. Use the 2024 average to make predictions for the 2025 transactions
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Calculate national yearly average
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "national_year_avg.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _axs = plt.subplots(1, 1, figsize=(10, 4))

    # Plot average price per year
    plt.plot(
        _df["year"],
        _df["mean_price"] / 1000,
        marker=".",
        color=palette[0],
        label="Mean",
    )
    plt.plot(
        _df["year"],
        _df["median"] / 1000,
        "--",
        color=palette[3],
        label="Median",
    )

    plt.fill_between(
        _df["year"],
        _df["q1"] / 1000,
        _df["q3"] / 1000,
        alpha=0.2,
        label="Inter-quartile range",
        color=palette[1],
    )

    plt.title("Aggregated transaction price")
    plt.xlabel("Year")
    plt.ylabel("Price (£1k)")
    plt.grid(axis="y")
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.legend()

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Estimate the relative value of each property

    For each property transaction, I divide the price paid by the yearly mean to calculate the price-market-ratio (PMR).
    The transactions for each property are aggregated to provide a per-property PMR, which is a time-independant measure of value.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    # TODO: add analysis on the proportion of mean here.... Distribution?
    # TODO: analyse the variance of them here -- that is an introduction to error estimation

    # TODO: show how I calculate the PMR for each transaction and then take the average for the house

    _data_path = mo.notebook_location() / "public" / "national_year_avg.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True)

    # Plot average price per year on the top subplot
    _axs[0].plot(
        _df["year"],
        _df["mean_price"] / 1000,
        marker=".",
        color=palette[0],
        label="National mean",
    )

    _data_path = mo.notebook_location() / "public" / "example_prediction.csv"
    _df2 = pd.read_csv(str(_data_path))

    # _axs[0].plot(
    #     _df2["year"],
    #     _df2["predicted_price"] / 1000,
    #     color=palette[1],
    #     label="Predicted price",
    # )
    _axs[0].plot(
        _df2["year"],
        _df2["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Transaction price",
    )

    # _axs[0].set_xlabel("Year")
    _axs[0].set_ylabel("Price (£1k)")
    _axs[0].grid(axis="y")
    _axs[0].spines["top"].set_visible(False)
    _axs[0].spines["right"].set_visible(False)
    _axs[0].legend()

    _transactions = _df2[_df2["price_paid"].notna()].merge(_df, on="year", how="left")
    _transactions["pmr"] = _transactions["price_paid"] / _transactions["mean_price"]

    _axs[1].bar(
        _transactions["year"],
        _transactions["pmr"] - 1,
        bottom=1,
        color=palette[2],
        label="PMR",
    )
    mean_pmr = _transactions["pmr"].mean()
    _axs[1].axhline(
        mean_pmr, color=palette[2], linewidth=1.5, linestyle="--", label="Mean PMR"
    )
    _axs[1].axhline(1, color="black", linewidth=1.5)
    _axs[1].set_ylabel("Price market ratio")
    _axs[1].set_xlabel("Year")
    _axs[1].set_ylim(0, 2)
    # _axs[1].set_ylim(0.4, 1.1)
    _axs[1].grid(axis="y")
    _axs[1].text(2020, 0.6, f"Mean PMR: {mean_pmr:.2f}")

    _axs[1].spines["top"].set_visible(False)
    _axs[1].spines["right"].set_visible(False)
    _axs[1].spines["bottom"].set_visible(False)
    _axs[1].legend(loc="upper left")

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Make Predictions for 2025

    The average property price of 2024, was £285,094. This average is multipled by each properties PMR.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "2025_predictions.csv"
    _df = pd.read_csv(_data_path)

    _fig, _ax = plt.subplots(figsize=(7, 2.5))

    _ax.hist(
        _df["predicted_price"] / 1000,
        bins=100,
        color=palette[0],
        label="Predicted Price",
    )
    plt.title("Distribution of Predicted Prices")
    plt.xlabel("Predicted Price")
    plt.ylabel("Frequency")

    _ax.set_xlabel("Predicted Price (£1k)")
    _ax.set_ylabel("Frequency")

    _mean_pred = _df["predicted_price"].mean() / 1000
    _ax.axvline(_mean_pred, color="gray", linestyle="--", alpha=0.6, label="Mean")
    _q1, _q3 = (_df["predicted_price"] / 1000).quantile([0.25, 0.75])
    _ax.axvspan(_q1, _q3, color=palette[5], alpha=0.2, label="IQR")
    _ax.legend(frameon=False)

    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)

    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Analyse Predictions

    For each prediction, the error is calculated as the absolute difference between the predicted price and the actual price. To make the errors comparable between properties of different values, the absolute error is divided by the actual price and multiplied by 100 to get the error percentage.
    """)
    return


@app.cell
def _(mo, pd):
    _data_path = mo.notebook_location() / "public" / "2025_predictions.csv"
    _df = pd.read_csv(_data_path)

    _df["abs_error"] = (_df["price_paid"] - _df["predicted_price"]).abs()
    _df["error_percentage"] = (_df["price_paid"] - _df["predicted_price"]).abs() / _df[
        "price_paid"
    ]

    mae = _df["error_percentage"].mean() * 100
    medae = _df["error_percentage"].median() * 100
    q1 = _df["error_percentage"].quantile(0.25) * 100
    q3 = _df["error_percentage"].quantile(0.75) * 100
    # most_accurate_prediction = _df.loc[_df["abs_error"].idxmin()]

    mo.md(f"""
    - Mean absolute error percentage: {mae:,.2f}%
    - Median absolute error percentage: {medae:,.2f}%
    - Interquartile range of error: {q1:,.2f}% to {q3:,.2f}%

    The mean predictions error per property is £{_df["abs_error"].mean():,.2f}
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Visualisation of accuracy

    The correlation of the predicted vs actual price is plotted to provide an intuitive sense of the accuracy of the predictions.
    Additionally, we plot a histogram showing the distributions of the absolute error percentages.
    """)
    return


@app.cell
def _(gaussian_kde, mo, np, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "2025_predictions.csv"
    _df = pd.read_csv(_data_path)

    xy = np.vstack([_df["price_paid"], _df["predicted_price"]]) / 1000
    z = gaussian_kde(xy)(xy)

    _fig, _axs = plt.subplots(1, 2, figsize=(12, 4))

    _axs[0].scatter(
        _df["price_paid"] / 1000,
        _df["predicted_price"] / 1000,
        s=5,
        c=z,
    )
    plt.sca(_axs[0])
    plt.ylim(0, 1e3)
    plt.title("Correlation of 2025 predictions")
    plt.xlabel("Price Paid (£1k)")
    plt.ylabel("Predicted Price (£1k)")

    _mean_paid = _df["price_paid"].mean() / 1000
    _mean_pred = _df["predicted_price"].mean() / 1000

    _axs[0].axvline(_mean_paid, color="gray", linestyle="--", alpha=0.6)
    _axs[0].axhline(_mean_pred, color="gray", linestyle="--", alpha=0.6)
    _axs[0].text(
        _mean_paid + 20,
        800,
        f"Mean\nPaid:\n£{_mean_paid:.1f}k",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.5, "edgecolor": "none"},
    )
    _axs[0].text(
        500,
        _mean_pred + 20,
        f"Mean Predicted: £{_mean_pred:.1f}k",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.5, "edgecolor": "none"},
    )

    _axs[0].set_aspect("equal", adjustable="box")
    _axs[0].spines["top"].set_visible(False)
    _axs[0].spines["right"].set_visible(False)

    _error_pct = (
        np.abs((_df["predicted_price"] - _df["price_paid"]) / _df["price_paid"]) * 100
    )
    _axs[1].hist(_error_pct, bins=50, range=(0, 100), color=palette[2])
    _axs[1].set_title("Absolute Error Percentage")
    _axs[1].set_xlabel("Error (%)")
    _axs[1].set_ylabel("Frequency")
    _axs[1].spines["top"].set_visible(False)
    _axs[1].spines["right"].set_visible(False)

    _mean_error = _error_pct.mean()
    _axs[1].axvline(_mean_error, color="gray", linestyle="--", alpha=0.6)
    _axs[1].text(
        _mean_error + 2,
        _axs[1].get_ylim()[1] * 0.8,
        f"Mean Error: {_mean_error:.1f}%",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.5, "edgecolor": "none"},
    )
    _median_error = _error_pct.median()
    _axs[1].axvline(_median_error, color="gray", linestyle="--", alpha=0.6)
    _axs[1].text(
        _median_error + 2,
        _axs[1].get_ylim()[1] * 0.6,
        f"Median Error: {_median_error:.1f}%",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.5, "edgecolor": "none"},
    )

    plt.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Example predictions

    To illustrate how the predictions are made, we show examples of the best and worst predictions.

    - **Best prediction**: The top graph shows that the purple cross (transaction in 2025) is very close to the predicted orange line. Visibly, this property has had a stable PMR over the years, and the prediction is therefore accurate.
    - **Worst prediction**: The bottom graph shows that the purple cross (transaction in 2025) is very close to the predicted orange line. The sale in 2025, was less than half what the property sold for previously, meaning that something unknown has occured with this property. This is more of a bad data point than a poor prediction, since it is impossible to predict such an event.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "national_year_avg.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True)

    # Plot average price per year on the top subplot
    for i in range(2):
        _axs[i].plot(
            _df["year"],
            _df["mean_price"] / 1000,
            marker=".",
            color=palette[0],
            label="National mean",
        )

    _data_path = mo.notebook_location() / "public" / "example_prediction_best.csv"
    _df1 = pd.read_csv(str(_data_path))

    _axs[0].plot(
        _df1["year"],
        _df1["predicted_price"] / 1000,
        color=palette[1],
        label="Predicted price",
    )
    _axs[0].plot(
        _df1["year"],
        _df1["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Transaction price",
    )

    # _axs[0].set_xlabel("Year")
    _axs[0].set_ylabel("Price (£1k)")
    _axs[0].grid(axis="y")
    _axs[0].spines["top"].set_visible(False)
    _axs[0].spines["right"].set_visible(False)
    _axs[0].legend(loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.2))
    _axs[0].set_ylim(0, 300)

    _data_path = mo.notebook_location() / "public" / "example_prediction_worst.csv"
    _df2 = pd.read_csv(str(_data_path))

    _axs[1].plot(
        _df2["year"],
        _df2["predicted_price"] / 1000,
        color=palette[1],
        label="Predicted price",
    )
    _axs[1].plot(
        _df2["year"],
        _df2["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Transaction price",
    )

    _axs[1].set_xlabel("Year")
    _axs[1].set_ylabel("Price (£1k)")
    _axs[1].grid(axis="y")
    _axs[1].spines["top"].set_visible(False)
    _axs[1].spines["right"].set_visible(False)

    x_pos = 2009
    y_pos = 260
    _axs[0].text(x_pos, y_pos, "Best prediction", fontweight="bold")
    _axs[1].text(x_pos, y_pos, "Worst prediction", fontweight="bold")

    plt.xlim(2008.5, 2025.5)

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Conclusion

    This project used historical price data to predict the selling price of properties in 2025. The price-market-ratio for each house was calculated and used to make a prediction. The method resulted in an accuracy of 13.23%.

    Future versions of the project plan to:
    1. Model improvements:
        - Estimate the confidence of the prediction, i.e. what error is due to property variance (irreducible) vs model bias (reducible)
        - Improve predictions by using the location (postcode) of each property
        - Use a rolling average rather than fixed yearly average
    2. Deploy database as DuckLake and automate database expansion
    3. Build interactive website that estimates the real-value of each property (depends on a deployed database)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Supplementary analysis (backtesting)

    The modelling approach was tested by using the same approach for each year that data was available. The mean errors plotted below show that the model consistently achieves between 10% - 15% errors through most years, with a spike after the 2008 crash.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "yearly_accuracy.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _axs = plt.subplots(1, 1, figsize=(10, 4))

    # Plot average price per year
    plt.plot(
        _df["year"],
        _df["mean_absolute_error_percentage"] * 100,
        marker="o",
        color=palette[0],
        label="Mean",
        linewidth=2,
    )

    plt.fill_between(
        _df["year"],
        _df["absolute_error_percentage_q1"] * 100,
        _df["absolute_error_percentage_q3"] * 100,
        alpha=0.2,
        label="Inter-quartile range",
        color=palette[1],
    )

    plt.title(
        "Historical yearly prediction accuracy", ha="left", x=0.02, y=1, va="center"
    )
    plt.xlabel("Year")
    plt.ylabel("Absolute error percentage")
    plt.grid(axis="y")
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.legend(ncol=2, frameon=False, bbox_to_anchor=(0.8, 1.1), loc="upper center")

    plt.tight_layout()
    _fig  # noqa: B018
    return


if __name__ == "__main__":
    app.run()
