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
    return (duckdb,)


@app.cell
def _(duckdb):
    con = duckdb.connect("../data/main.db")

    df = con.sql("""
        SELECT * FROM year_avg_data
    """).df()

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
