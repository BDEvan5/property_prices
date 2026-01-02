import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    import numpy as np

    import matplotlib.pyplot as plt
    import duckdb
    import pandas as pd

    import os
    if os.getcwd().endswith("property_prices/property_prices"):
        os.chdir("..")

    return duckdb, pd, plt


@app.cell
def _(mo):
    mo.md(r"""
    ## Aggregate dataset (by year)
    """)
    return


@app.cell
def _(duckdb):

    con = duckdb.connect("data/main.db")

    con.sql("DROP TABLE IF EXISTS year_avg_data")
    con.sql("""
        CREATE TABLE year_avg_data (
            year INT,
            avg_price INT,
            sales_count INT
        )
    """)

    return (con,)


@app.cell
def _(con):

    con.sql("""
        INSERT INTO year_avg_data (year, avg_price, sales_count) FROM (
            SELECT 
                year(deed_date) as year,
                AVG(price_paid) as avg_price,
                COUNT(*) as sales_count
            FROM transactions
            GROUP BY year
            ORDER BY year
        )
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT * FROM year_avg_data
    """).df()


    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Save to CSV
    """)
    return


@app.cell
def _(con):
    df = con.sql("SELECT * FROM year_avg_data").df()
    df.to_csv("web/public/avg_yearly_sales.csv", index=False)
    df.to_csv("web/public/avg_yearly_sales.csv.gz", index=False, compression="gzip")
    print(df.shape)
    df.sample(5)
    return (df,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Plot
    """)
    return


@app.cell
def _(df, plt):

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    # Plot average price per year
    axs[0].plot(df["year"], df["avg_price"] / 1000, marker="o", color="royalblue")
    axs[0].set_title("Average Price per Year")
    axs[0].set_xlabel("Year")
    axs[0].set_ylabel("Average Price (£1k)")
    axs[0].grid(True)

    # Plot sales count per year
    axs[1].bar(df["year"], df["sales_count"], color="salmon")
    axs[1].set_title("Sales Count per Year")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Sales Count")
    axs[1].grid(axis="y")

    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Explore interest rate correlation
    """)
    return


@app.cell
def _(pd):
    df_interest = pd.read_csv("data/interest_rates.csv")

    df_interest["change_date"] = pd.to_datetime(df_interest["Date Changed"], format="%d %b %y")
    df_interest = df_interest.rename(columns={"Rate": "rate"}).drop("Date Changed", axis=1)
    df_interest = df_interest.sort_values('change_date')
    df_interest.head(2)
    return (df_interest,)


@app.cell
def _(df, df_interest, pd, plt):
    _fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(12, 10))

    df["date"] = pd.to_datetime(df["year"].astype(str) + '-01-01')

    # Plot Property Prices
    ax1.plot(df['date'], df['avg_price'], color='blue', label='Property Price')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    ax1.set_title('Property Market Trends')

    # Plot Sales Volume
    ax2.bar(df['date'], df['sales_count'], color='green', label='Sales Volume', width=300)
    ax2.set_ylabel('Volume')
    ax2.legend(loc='upper left')

    # Plot Interest Rate
    ax3.plot(df_interest['change_date'], df_interest['rate'], color='red', label='Interest Rate', drawstyle='steps-post')
    ax3.set_ylabel('Interest Rate (%)')
    ax3.set_xlabel('Date')
    ax3.legend(loc='upper left')

    plt.xlim(df['date'].min(), df['date'].max())

    plt.tight_layout()
    plt.show()

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
