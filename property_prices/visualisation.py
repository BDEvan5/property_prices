import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell
def _():
    import duckdb
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    return duckdb, np, pd, plt


@app.cell
def _():
    DATABASE_PATH = "../data/properties.db"
    return (DATABASE_PATH,)


@app.cell
def _(DATABASE_PATH, duckdb):
    _con = duckdb.connect(DATABASE_PATH)
    yearly_data_hpi = _con.sql("SELECT * from hpi_national_year_avg").df()
    yearly_data = _con.sql("SELECT * from national_year_avg").df()
    _con.close()
    yearly_data.head()
    return yearly_data, yearly_data_hpi


@app.cell
def _(plt, yearly_data, yearly_data_hpi):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

    # Plot 1: Volume
    ax1.bar(
        yearly_data["year"],
        yearly_data["volume"],
        color="lightgrey",
        alpha=0.6,
        width=0.5,
    )
    ax1.bar(
        yearly_data_hpi["year"],
        yearly_data_hpi["volume"],
        color="tab:blue",
        alpha=0.6,
        width=0.5,
    )
    ax1.set_ylabel("Volume")
    ax1.set_title("Yearly Property Market: Volume")

    # Plot 2: Average Price
    ax2.plot(yearly_data["year"], yearly_data["mean_price"], "-o", color="tab:blue")
    ax2.plot(
        yearly_data_hpi["year"], yearly_data_hpi["mean_price"], "-o", color="tab:orange"
    )
    ax2.set_ylabel("Average Price")
    ax2.set_title("Yearly Property Market: Average Price")

    # Plot 3: Price Standard Deviation
    ax3.plot(yearly_data["year"], yearly_data["std_price"], "-o", color="tab:orange")
    ax3.plot(
        yearly_data_hpi["year"], yearly_data_hpi["std_price"], "-o", color="tab:blue"
    )
    ax3.set_ylabel("Price Std Dev")
    ax3.set_xlabel("Year")
    ax3.set_title("Yearly Property Market: Price Standard Deviation")

    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Analyse transaction densities
    """)
    return


@app.cell
def _(duckdb):
    year = 2015

    _con = duckdb.connect("../data/_properties.db")
    df = _con.sql(f"SELECT * from transactions where year(deed_date) = {year}").df()
    _con.close()
    df.head()
    return (df,)


@app.cell
def _():
    # print(df[df["price_paid"] < 10000].shape[0])
    return


@app.cell
def _(df, np, plt):
    data = df["price_paid"]
    print(f"99th percentile: {np.percentile(data, 99):.2f}")
    data = data[data < np.percentile(data, 99)]

    values, bins = np.histogram(data, bins=50)
    bin_width = bins[1] - bins[0]

    plt.bar(bins[:-1], values, width=bin_width)
    # plt.gca().set_xscale('log')

    mean = data.mean()
    std = data.std()
    plt.axvline(mean, color="r", linestyle="--", label=f"Mean: {mean:.2f}")
    plt.axvspan(
        mean - std, mean + std, color="r", alpha=0.2, label=f"Std Dev: {std:.2f}"
    )

    plt.gca().set_yscale("log")
    plt.xlabel("Price Paid")
    plt.ylabel("Frequency")
    plt.legend()
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Plot errors
    """)
    return


@app.cell
def _(DATABASE_PATH, duckdb, pd, plt, yearly_data_hpi):
    _con = duckdb.connect(DATABASE_PATH)
    _properties = _con.sql(
        "select * from properties where property_id in (select property_id from hpi_transaction_predictions group by property_id having count(*) >3 order by sum(abs(error)) asc limit 6);"
    ).df()

    hpi_dates = pd.to_datetime(yearly_data_hpi["year"], format="%Y")
    _fig, _axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
    _axes = _axes.flatten()

    for _i in range(6):
        if _i >= len(_properties):
            _axes[_i].set_visible(False)
            continue

        _ax = _axes[_i]
        _property_id = _properties.iloc[_i]["property_id"]
        _property_label = ";".join(
            _properties.iloc[_i][["paon", "saon", "street", "locality", "postcode"]]
        )

        # plot transactions
        _df = _con.sql(
            f"select * from transactions where property_id = '{_property_id}'"
        ).df()
        _df = _df.sort_values(by="deed_date")
        _ax.plot(
            _df["deed_date"].values,
            _df["price_paid"].values,
            "-x",
            label=_property_label,
        )

        # Plot prediction
        _df = _con.sql(
            f"select * from hpi_predictions where property_id = '{_property_id}'"
        ).df()
        _ax.plot(
            pd.to_datetime(_df["year"], format="%Y"),
            _df["predicted_price"],
            label="Prediction",
        )

        # Plot HPI
        _ax.plot(
            hpi_dates,
            yearly_data_hpi["mean_price"],
            "-o",
            color="tab:orange",
            label="HPI Mean",
        )
        _ax.legend()

    _con.close()
    plt.suptitle("Example predictions (most accurate)")
    plt.tight_layout()
    plt.show()
    return (hpi_dates,)


@app.cell
def _(DATABASE_PATH, duckdb, hpi_dates, pd, plt, yearly_data_hpi):
    _con = duckdb.connect(DATABASE_PATH)
    _properties = _con.sql(
        "select * from properties where property_id in (select property_id from hpi_transaction_predictions group by property_id having count(*) >3 order by sum(abs(error)) desc limit 6);"
    ).df()

    _fig, _axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
    _axes = _axes.flatten()

    for _i in range(6):
        if _i >= len(_properties):
            _axes[_i].set_visible(False)
            continue

        _ax = _axes[_i]
        _property_id = _properties.iloc[_i]["property_id"]
        _property_label = ";".join(
            _properties.iloc[_i][["paon", "saon", "street", "locality", "postcode"]]
        )

        # plot transactions
        _df = _con.sql(
            f"select * from transactions where property_id = '{_property_id}'"
        ).df()
        _df = _df.sort_values(by="deed_date")
        _ax.plot(
            _df["deed_date"].values,
            _df["price_paid"].values,
            "-x",
            label=_property_label,
        )

        # Plot prediction
        _df = _con.sql(
            f"select * from hpi_predictions where property_id = '{_property_id}'"
        ).df()
        _ax.plot(
            pd.to_datetime(_df["year"], format="%Y"),
            _df["predicted_price"],
            label="Prediction",
        )

        # Plot HPI
        _ax.plot(
            hpi_dates,
            yearly_data_hpi["mean_price"],
            "-o",
            color="tab:orange",
            label="HPI Mean",
        )
        _ax.legend()

    _con.close()
    plt.suptitle("Example predictions (least accurate)")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(DATABASE_PATH, duckdb, hpi_dates, pd, plt, yearly_data_hpi):
    _con = duckdb.connect(DATABASE_PATH)
    _properties = _con.sql(
        "select * from properties where property_id in (select property_id from transactions group by property_id having count(*) >7);"
    ).df()

    _fig, _axes = plt.subplots(3, 2, figsize=(16, 12), sharex=True)
    _axes = _axes.flatten()

    for _i in range(6):
        if _i >= len(_properties):
            _axes[_i].set_visible(False)
            continue

        _ax = _axes[_i]
        _property_id = _properties.iloc[_i]["property_id"]
        _property_label = ";".join(
            _properties.iloc[_i][["paon", "saon", "street", "locality", "postcode"]]
        )

        # plot transactions
        _df = _con.sql(
            f"select * from transactions where property_id = '{_property_id}'"
        ).df()
        _df = _df.sort_values(by="deed_date")
        _ax.plot(
            _df["deed_date"].values,
            _df["price_paid"].values,
            "-x",
            label=_property_label,
        )

        # Plot prediction
        _df = _con.sql(
            f"select * from hpi_predictions where property_id = '{_property_id}'"
        ).df()
        _ax.plot(
            pd.to_datetime(_df["year"], format="%Y"),
            _df["predicted_price"],
            label="Prediction",
        )

        # Plot HPI
        _ax.plot(
            hpi_dates,
            yearly_data_hpi["mean_price"],
            "-o",
            color="tab:orange",
            label="HPI Mean",
        )
        _ax.legend()

    _con.close()
    plt.suptitle("Example predictions (many transactions)")
    plt.tight_layout()
    plt.show()
    return


if __name__ == "__main__":
    app.run()
