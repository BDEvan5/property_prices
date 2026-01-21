import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell
def _():
    import duckdb
    import numpy as np
    import pandas as pd

    return duckdb, np, pd


@app.cell
def _():
    DATABASE_PATH = "../data/properties.db"
    data_path = "../web/public"
    return DATABASE_PATH, data_path


@app.cell
def _(DATABASE_PATH, data_path, duckdb, np, pd):
    def get_transaction_summary():
        con = duckdb.connect(DATABASE_PATH)
        df = con.execute("select * from transactions").df()
        con.close()

        bins = np.linspace(0, 1e6, 101)
        values, bins = np.histogram(df["price_paid"], bins=bins)
        hist_df = pd.DataFrame(
            {"bin_start": bins[:-1], "bin_end": bins[1:], "count": values}
        )

        return hist_df

    hist_df = get_transaction_summary()

    hist_df.to_csv(f"{data_path}/price_distribution.csv.gz", index=False)
    hist_df.to_csv(f"{data_path}/price_distribution.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb, pd):
    def get_database_statistics():
        con = duckdb.connect(DATABASE_PATH)
        df = con.execute("select * from transactions").df()
        con.close()

        n_transactions = len(df)
        n_properties = len(df["property_id"].unique())
        mean_price = df["price_paid"].mean()
        std_price = df["price_paid"].std()
        metrics_df = pd.DataFrame(
            {
                "n_transactions": [n_transactions],
                "n_properties": [n_properties],
                "mean_price": [mean_price],
                "std_price": [std_price],
            }
        ).T

        return metrics_df

    metrics_df = get_database_statistics()
    metrics_df.to_csv(f"{data_path}/transaction_summary.csv.gz", header=False)
    metrics_df.to_csv(f"{data_path}/transaction_summary.csv", header=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_national_yearly_avg():
        con = duckdb.connect(DATABASE_PATH)
        df = con.execute("select * from national_year_avg").df()
        con.close()
        return df

    national_avg_df = get_national_yearly_avg()
    national_avg_df.to_csv(f"{data_path}/avg_yearly_sales.csv.gz", index=False)
    national_avg_df.to_csv(f"{data_path}/avg_yearly_sales.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_hpi_national_yearly_avg():
        con = duckdb.connect(DATABASE_PATH)
        df = con.execute("select * from hpi_national_year_avg").df()
        con.close()
        return df

    hpi_national_avg_df = get_hpi_national_yearly_avg()
    hpi_national_avg_df.to_csv(f"{data_path}/hpi_avg_yearly_sales.csv.gz", index=False)
    hpi_national_avg_df.to_csv(f"{data_path}/hpi_avg_yearly_sales.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_hpi_accuracy():
        con = duckdb.connect(DATABASE_PATH)
        df = con.execute("select * from hpi_accuracy").df()
        con.close()
        return df

    hpi_accuracy_df = get_hpi_accuracy()
    hpi_accuracy_df.to_csv(f"{data_path}/hpi_accuracy.csv.gz", index=False)
    hpi_accuracy_df.to_csv(f"{data_path}/hpi_accuracy.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_best_prediction_examples():
        con = duckdb.connect(DATABASE_PATH)
        df = con.sql(
            "select * from properties where property_id in (select property_id from hpi_transaction_predictions group by property_id having count(*) >3 order by sum(abs(error)) asc limit 6);"
        ).df()
        con.close()
        return df

    best_predictions_df = get_best_prediction_examples()
    best_predictions_df.to_csv(f"{data_path}/best_predictions.csv.gz", index=False)
    best_predictions_df.to_csv(f"{data_path}/best_predictions.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_worst_prediction_examples():
        con = duckdb.connect(DATABASE_PATH)
        df = con.sql(
            "select * from properties where property_id in (select property_id from hpi_transaction_predictions group by property_id having count(*) >3 order by sum(abs(error)) asc limit 6);"
        ).df()
        con.close()
        return df

    worst_predictions_df = get_worst_prediction_examples()
    worst_predictions_df.to_csv(f"{data_path}/worst_predictions.csv.gz", index=False)
    worst_predictions_df.to_csv(f"{data_path}/worst_predictions.csv", index=False)
    return


@app.cell
def _(DATABASE_PATH, data_path, duckdb):
    def get_prediction_examples_with_many_transactions():
        con = duckdb.connect(DATABASE_PATH)
        df = con.sql(
            "select * from properties where property_id in (select property_id from transactions group by property_id having count(*) >7);"
        ).df()
        con.close()
        return df

    prediction_examples_df = get_prediction_examples_with_many_transactions()
    prediction_examples_df.to_csv(
        f"{data_path}/predictions_with_many_transactions.csv.gz", index=False
    )
    prediction_examples_df.to_csv(
        f"{data_path}/predictions_with_many_transactions.csv", index=False
    )
    return


if __name__ == "__main__":
    app.run()
