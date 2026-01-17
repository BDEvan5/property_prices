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
