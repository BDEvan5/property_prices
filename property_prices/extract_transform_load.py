import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Move raw data into duckdb
    """)
    return


@app.cell
def _():
    import pandas as pd
    from pathlib import Path

    import duckdb

    import os
    if os.getcwd().endswith("property_prices/property_prices"):
        os.chdir("..")

    con = duckdb.connect("data/main.db")
    DATA_DIR = Path("data/raw_land_registry")
    return DATA_DIR, con, pd


@app.cell
def _(mo):
    mo.md(r"""
    ## Extract
    """)
    return


@app.cell
def _(DATA_DIR, pd):
    df = pd.read_csv(f"{DATA_DIR}/TA11.csv")

    address_cols = ["paon", "saon", "street", "locality", "town", "postcode"]
    df["address"] = df[address_cols].apply(
        lambda x: ";".join([str(xi) for xi in x]).replace("nan;", ""), axis=1
    )

    df.head(2)
    return address_cols, df


@app.cell
def _(df):
    print(df["property_type"].unique())
    print(df["new_build"].unique())
    print(df["estate_type"].unique())
    print(df["transaction_category"].unique())
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Transform & Load properties
    """)
    return


@app.cell
def _(address_cols, df):
    property_columns = address_cols + ["address", "district", "county"]
    df_properties = df[property_columns].drop_duplicates(subset=["address"]).reset_index(drop=True)
    print(len(df_properties["address"]), df_properties["address"].nunique())
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Load (into db)
    """)
    return


@app.cell
def _(con):
    con.sql("DROP TABLE IF EXISTS properties")
    con.sql("DROP SEQUENCE IF EXISTS properties_id_seq")

    # Create squence & table
    con.sql("CREATE SEQUENCE properties_id_seq START 1")
    con.sql("""
        CREATE TABLE properties (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('properties_id_seq'),
            paon VARCHAR,
            saon VARCHAR,
            street VARCHAR,
            locality VARCHAR,
            town VARCHAR,
            postcode VARCHAR,
            district VARCHAR,
            county VARCHAR,
            address VARCHAR,
        )
    """)
    return


@app.cell
def _(con):
    con.sql("""
        INSERT INTO properties (paon, saon, street, locality, town, postcode, address)
        SELECT paon, saon, street, locality, town, postcode, address FROM df_properties
    """)
    return


@app.cell
def _(con):
    con.sql("SELECT * FROM properties").df().sample(5)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Transform & Load transactions
    """)
    return


@app.cell
def _(df, pd):
    df_transactions = df[["address", "deed_date", "price_paid", "property_type", "new_build", "estate_type", "transaction_category", "unique_id"]].copy()
    df_transactions["deed_date"] = pd.to_datetime(df_transactions["deed_date"])

    df_transactions.head(2)
    return (df_transactions,)


@app.cell
def _(con):
    con.sql("DROP TABLE IF EXISTS transactions")
    con.sql("DROP SEQUENCE IF EXISTS transactions_id_seq")

    # Create squence & table
    con.sql("CREATE SEQUENCE transactions_id_seq START 1")
    con.sql("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY DEFAULT NEXTVAL('transactions_id_seq'),
            address VARCHAR,
            deed_date DATE,
            price_paid INTEGER,
            property_type CHAR,
            estate_type CHAR,
            new_build CHAR,
            transaction_category CHAR,
            unique_id VARCHAR
        )
    """)

    return


@app.cell
def _(con):
    # read df into db
    con.sql("""
        INSERT INTO transactions (address, deed_date, price_paid, property_type, new_build, estate_type, transaction_category, unique_id)
        SELECT address, deed_date, price_paid, property_type, new_build, estate_type, transaction_category, unique_id FROM df_transactions
    """)
    return


@app.cell
def _(con):
    con.sql("SELECT * FROM transactions").df().sample(5)

    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Record statistics
    """)
    return


@app.cell
def _(df_transactions):
    transaction_summary = df_transactions["price_paid"].describe(percentiles=[0.5])
    transaction_summary.to_csv("web/publictransaction_summary.csv")
    transaction_summary
    return


if __name__ == "__main__":
    app.run()
