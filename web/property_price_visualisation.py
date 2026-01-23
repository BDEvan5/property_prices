import marimo

__generated_with = "0.19.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    palette = plt.get_cmap("Set2").colors
    return mo, np, palette, pd, plt


@app.cell
def _(mo):
    mo.md("""
    # Property Price Prediction


    > **Challenge:**
    >
    > Predict the transaction value for each property that was sold in 2025, using all the data until the end of 2024.
    > The properties to predict are filtered to include residential transactions, with at least 1 previous sale (of the same estate type) and a value of less than £1M.

    This prediction method can then be applied to estimate the current value of every property in the UK.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Database Statistics (raw data)
    Transaction data for every property transaction since 1995 is downloaded from [HM Land Registry](https://landregistry.data.gov.uk/).
    The raw data is loaded into a SQL database (DuckDB) and transformed to have properties and transactions tables.
    """)
    return


@app.cell
def _(mo, np, pd, plt):
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

    The raw data above is cleaned for training and prediction by applying the following filters:
    - Prices below £1M and above £10k
    - Remove type 'B' commercial transactions
    - Houses with constant property types, i.e. remove changes from plot () to house () # I don't think we need this? (D, T, S, O)
    - Remove houses with multiple transactions on the same day
    """)
    return


@app.cell
def _():
    # TODO: add statistics on the 2025 prediction challenge. How many properties are there?
    # - how many property transactions do I pick each year compared to all transactions
    # - Add a distribution of transactions for the 2025 challenge, or barplot per year or something
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
    ### Calculate national yearly average
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    # TODO: add IQR for the average and possibly remove the volume
    # Move the volume to the database statistic above for the 2025 challenge

    data_path = mo.notebook_location() / "public" / "avg_yearly_sales.csv"
    _df = pd.read_csv(str(data_path))
    hpi_data_path = mo.notebook_location() / "public" / "hpi_avg_yearly_sales.csv"
    _df_hpi = pd.read_csv(str(hpi_data_path))

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
    mo.md(r"""
    ### Estimate the relative value of each property

    For each property transaction, I divide the price paid by the yearly mean to calculate the price-market-ratio (PMR).
    The transactions for each property are aggregated to provide a per-property PMR, which is a time-independant measure of value.
    """)
    return


@app.cell
def _():
    # TODO: add analysis on the proportion of mean here.... Distribution?
    # TODO: analyse the variance of them here -- that is an introduction to error estimation

    # TODO: show how I calculate the PMR for each transaction and then take the average for the house

    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Make Predictions for 2025

    The average property price of 2024, was £XXX,XXX. This average is multipled by each properties PMR
    """)
    return


@app.cell
def _():
    # TODO: show distribution of all predictions
    # Calculate what the 2025 mean would be?
    # Show a correlation plot - that can look cool
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Analyse predictions

    The predictions are analysed by:
    - Filtering them to properties that actually sold in 2025
    - Calculating the prediction accuracy
    - Investigating the distribution of errors
    - Showing example predictions (best & worst)
    """)
    return


@app.cell
def _():
    # TODO: filter transactions and show a pie chart or something simple.
    return


@app.cell
def _():
    # Calculate total predictions accuracy
    return


@app.cell
def _():
    # Show distribution of errors to explain the accuracy
    return


@app.cell
def _():
    # Show example predictions for best and worst
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Conclusion

    This project used historical price data to predict the selling price of properties in 2025. The price-market-ratio for each house was calculated and used to make a prediction. The method resulted in an accuracy of XX%.

    Future versions of the project plan to:
    - Model improvements:
        - Estimate the confidence of the prediction, i.e. what error is due to property variance (irreducible) vs model bias (reducible)
        - Improve predictions by using the location (postcode) of each property
        - Use a rolling average rather than fixed yearly average
    - Deploy database as DuckLake and automate database expansion
    - Build interactive website that estimates the real-value of each property
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Supplementary analysis

    Additional analysis that was performed, but is not essential:
    - Historical accuracy
    - Examples with many transactions
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
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
    data_path = mo.notebook_location() / "public" / "avg_yearly_sales.csv"
    _df = pd.read_csv(str(data_path))
    hpi_data_path = mo.notebook_location() / "public" / "hpi_avg_yearly_sales.csv"
    _df_hpi = pd.read_csv(str(hpi_data_path))

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

    NOTE: the transactions are filtered to remove houses above £1M and below £10,000 since these transactions are outliers and a more complex model is required to predict their prices.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    data_path_accuracy = mo.notebook_location() / "public" / "hpi_accuracy.csv"
    hpi_accuracy = pd.read_csv(str(data_path_accuracy))

    _fig, ax = plt.subplots(1, 1, figsize=(7, 3))

    ax.plot(
        hpi_accuracy["year"],
        hpi_accuracy["mean_error_percentage"] * 100,
        color=palette[0],
        linewidth=2,
    )
    ax.set_title("HPI Mean Error Percentage")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Error Percentage (%)")
    ax.grid(axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    _fig  # noqa: B018
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Examples

    To better understand where the model is successful, several examples are plotted in three categories:

    1. Best predictions
    2. Worst predictions
    3. Properties with many transactions
    """)
    return


@app.cell
def _():
    # hpi_dates = pd.to_datetime(yearly_data_hpi["year"], format="%Y")
    # _fig, _axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
    # _axes = _axes.flatten()

    # for _i in range(6):
    #     if _i >= len(_properties):
    #         _axes[_i].set_visible(False)
    #         continue

    #     _ax = _axes[_i]
    #     _property_id = _properties.iloc[_i]["property_id"]
    #     _property_label = ";".join(
    #         _properties.iloc[_i][["paon", "saon", "street", "locality", "postcode"]]
    #     )

    #     # plot transactions
    #     _df = _con.sql(
    #         f"select * from transactions where property_id = '{_property_id}'"
    #     ).df()
    #     _df = _df.sort_values(by="deed_date")
    #     _ax.plot(
    #         _df["deed_date"].values,
    #         _df["price_paid"].values,
    #         "-x",
    #         label=_property_label,
    #     )

    #     # Plot prediction
    #     _df = _con.sql(
    #         f"select * from hpi_predictions where property_id = '{_property_id}'"
    #     ).df()
    #     _ax.plot(
    #         pd.to_datetime(_df["year"], format="%Y"),
    #         _df["predicted_price"],
    #         label="Prediction",
    #     )

    #     # Plot HPI
    #     _ax.plot(
    #         hpi_dates,
    #         yearly_data_hpi["mean_price"],
    #         "-o",
    #         color="tab:orange",
    #         label="HPI Mean",
    #     )
    #     _ax.legend()

    # _con.close()
    # plt.suptitle("Example predictions (most accurate)")
    # plt.tight_layout()
    # plt.show()
    return


@app.cell
def _():
    # data_path_accuracy = mo.notebook_location() / "public" / "hpi_accuracy.csv"
    # hpi_accuracy = pd.read_csv(str(data_path_accuracy))

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
    ## Conclusion

    This v0.2 project analyses a dataset of property transactions in the UK.

    Future versions of the project plan to:
    - Develop a model to estimate individual property prices
    - Use a more complex model to predict prices
    - Automate dataset expansion, model prediction & accuracy tracking
    - Take other information into account, such as the interest rate
    """)
    return


if __name__ == "__main__":
    app.run()
