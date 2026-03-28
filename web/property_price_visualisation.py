import marimo

__generated_with = "0.20.4"
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
    # UK property prices: SQL pipeline and price–market baselines

    **Portfolio project:** [HM Land Registry](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads) transactions in **DuckDB**, modelled in **SQL** (national vs outward-area aggregates) with **Python** for evaluation and this page.

    *Holdout:* per-property PMR is fit on sales **before 2025**; **2025** transactions are scored for error. [Code on GitHub](https://github.com/bdevan5/property_prices).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Data at a glance
    Raw CSVs are loaded into DuckDB, normalised into `properties` and `transactions`, and joined to a postcode **area** table for regional aggregates.
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
    - Transactions: {int(_df.loc["n_transactions"].item()):,}
    - Properties: {int(_df.loc["n_properties"].item()):,}
    - Mean price (all transactions): £{float(_df.loc["mean_price"].item()):,.0f} (std {float(_df.loc["std_price"].item()):,.0f})
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
    plt.title("Distribution of transaction prices")
    plt.xlabel("Price paid (£)")
    plt.ylabel("Count")
    xtick_marks = np.arange(0, _df_distribution["bin_end"].max() + 1, 200000)
    plt.xticks(xtick_marks, [f"{int(x / 1000)}k" for x in xtick_marks])

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    mo.hstack([_fig, md_element])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Cleaning for modelling

    **Evaluation setup:** predict **2025** sales using information up to **2024** (PMR fit uses pre-2025 transactions only in the SQL pipeline).

    Filters applied to transactions:
    - Price between £10k and £1M
    - Residential only; exclude commercial (type B)
    - Constant property type per property
    - Drop same-day duplicate sales
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _df = pd.read_csv(
        str(mo.notebook_location()) + "/public/transactions_cleaned_by_year.csv",
        header=0,
    )

    _fig, _ax = plt.subplots(figsize=(8, 3))

    _ax.bar(
        _df["transaction_year"] - 0.2,
        _df["count_all"],
        color=palette[3],
        label="All",
        width=0.4,
    )
    _ax.bar(
        _df["transaction_year"] + 0.2,
        _df["count_cleaned"],
        color=palette[2],
        label="Cleaned",
        width=0.4,
    )

    _ax.set_title("Transactions per year")
    _ax.set_xlabel("Year")
    _ax.set_ylabel("Count")
    _ax.grid(axis="y")
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend()

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Modelling approach

    I assume a property’s **price–market ratio** (PMR)—price relative to the previous year’s market mean—is stable over time. That is a strong simplification; there is no information on condition, extensions, or micro-location.

    **Two baselines in SQL:**
    1. **National:** prior-year **UK** mean × mean PMR.
    2. **Outward area:** prior-year mean for the postcode **area** (e.g. `SW`) × mean PMR.

    Steps: (1) yearly aggregates, (2) per-transaction PMR and per-property average PMR from pre-2025 sales, (3) multiply by the relevant prior-year mean for each actual sale year (including 2025).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 1. National market context
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "national_year_avg.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _ax = plt.subplots(1, 1, figsize=(10, 4))

    _ax.plot(
        _df["year"],
        _df["mean_price"] / 1000,
        marker=".",
        color=palette[0],
        label="Mean",
    )
    _ax.plot(
        _df["year"],
        _df["median"] / 1000,
        "--",
        color=palette[3],
        label="Median",
    )

    _ax.fill_between(
        _df["year"],
        _df["q1"] / 1000,
        _df["q3"] / 1000,
        alpha=0.2,
        label="Inter-quartile range",
        color=palette[1],
    )

    _ax.set_title("UK aggregate prices (cleaned transactions)")
    _ax.set_xlabel("Year")
    _ax.set_ylabel("Price (£1k)")
    _ax.grid(axis="y")
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend()

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 2. Example property: national vs area PMR

    Same property (most sales in the cleaned set): **left** = UK mean; **right** = outward **area** mean (e.g. `SW`). Lower panels: PMR = price ÷ that year’s mean. Each baseline uses the **mean PMR** (with prior-year means) when forecasting—area tracks local market conditions; national smooths geography.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _pub = mo.notebook_location() / "public"
    _df_nat = pd.read_csv(_pub / "national_year_avg.csv")
    _df_area = pd.read_csv(_pub / "example_area_year_avg.csv")
    _df2 = pd.read_csv(_pub / "example_prediction.csv")
    _area_code = str(_df_area["area"].iloc[0])

    _fig, _axs = plt.subplots(2, 2, figsize=(11, 5), sharex="col")

    _axs[0, 0].plot(
        _df_nat["year"],
        _df_nat["mean_price"] / 1000,
        marker=".",
        color=palette[0],
        label="UK mean",
    )
    _axs[0, 0].plot(
        _df2["year"],
        _df2["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Sale price",
    )
    _axs[0, 0].set_ylabel("Price (£1k)")
    _axs[0, 0].set_title("National context")
    _axs[0, 0].grid(axis="y")
    _axs[0, 0].spines["top"].set_visible(False)
    _axs[0, 0].spines["right"].set_visible(False)
    _axs[0, 0].legend(loc="upper left", fontsize=8)

    _axs[0, 1].plot(
        _df_area["year"],
        _df_area["mean_price"] / 1000,
        marker=".",
        color=palette[4],
        label=f"Area mean ({_area_code})",
    )
    _axs[0, 1].plot(
        _df2["year"],
        _df2["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Sale price",
    )
    _axs[0, 1].set_title(f"Area context ({_area_code})")
    _axs[0, 1].grid(axis="y")
    _axs[0, 1].spines["top"].set_visible(False)
    _axs[0, 1].spines["right"].set_visible(False)
    _axs[0, 1].legend(loc="upper left", fontsize=8)

    _tn = _df2[_df2["price_paid"].notna()].merge(_df_nat, on="year", how="inner")
    _tn["pmr"] = _tn["price_paid"] / _tn["mean_price"]
    _mean_nat = _tn["pmr"].mean()
    _axs[1, 0].bar(
        _tn["year"],
        _tn["pmr"] - 1,
        bottom=1,
        color=palette[2],
        label="PMR",
    )
    _axs[1, 0].axhline(
        _mean_nat, color=palette[2], linestyle="--", linewidth=1.5, label="Mean PMR"
    )
    _axs[1, 0].axhline(1, color="black", linewidth=1)
    _axs[1, 0].set_ylabel("Price / UK mean")
    _axs[1, 0].set_ylim(0, 2)
    _axs[1, 0].grid(axis="y")
    _axs[1, 0].text(
        0.05,
        0.12,
        f"Mean PMR: {_mean_nat:.2f}",
        transform=_axs[1, 0].transAxes,
        fontsize=9,
    )
    _axs[1, 0].spines["top"].set_visible(False)
    _axs[1, 0].spines["right"].set_visible(False)
    _axs[1, 0].legend(loc="upper left", fontsize=8)

    _ta = _df2[_df2["price_paid"].notna()].merge(_df_area, on="year", how="inner")
    _ta["pmr"] = _ta["price_paid"] / _ta["mean_price"]
    _mean_ar = _ta["pmr"].mean()
    _axs[1, 1].bar(
        _ta["year"],
        _ta["pmr"] - 1,
        bottom=1,
        color=palette[2],
        label="PMR",
    )
    _axs[1, 1].axhline(
        _mean_ar, color=palette[2], linestyle="--", linewidth=1.5, label="Mean PMR"
    )
    _axs[1, 1].axhline(1, color="black", linewidth=1)
    _axs[1, 1].set_ylabel("Price / area mean")
    _axs[1, 1].set_xlabel("Year")
    _axs[1, 1].set_ylim(0, 2)
    _axs[1, 1].grid(axis="y")
    _axs[1, 1].text(
        0.05,
        0.12,
        f"Mean PMR: {_mean_ar:.2f}",
        transform=_axs[1, 1].transAxes,
        fontsize=9,
    )
    _axs[1, 1].spines["top"].set_visible(False)
    _axs[1, 1].spines["right"].set_visible(False)
    _axs[1, 1].legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo, pd):
    _nat = pd.read_csv(mo.notebook_location() / "public" / "national_year_avg.csv")
    _m2024 = float(_nat.loc[_nat["year"] == 2024, "mean_price"].iloc[0])
    mo.md(
        f"""
    ### 3. 2025 holdout predictions

    For each 2025 sale, predicted price = prior-year mean × fitted mean PMR. The **national** baseline uses the **{2024}** UK mean (£{_m2024:,.0f}) times each property’s PMR; the **area** baseline uses the prior-year mean for that property’s outward area.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2025 accuracy (holdout)

    Error is absolute percentage: |actual − predicted| / actual. Below: **national** and **outward-area** baselines on the same 2025 sales set (where the area model applies).
    """)
    return


@app.cell
def _(mo, pd):
    _m = pd.read_csv(mo.notebook_location() / "public" / "holdout_2025_metrics.csv")
    _n = _m[_m["model"] == "national"].iloc[0]
    _a = _m[_m["model"] == "area"].iloc[0]

    mo.md(f"""
    | Metric | National | Area |
    |--------|--------:|-----:|
    | Mean abs. error % | {float(_n["mean_abs_error_pct"]) * 100:.2f}% | {float(_a["mean_abs_error_pct"]) * 100:.2f}% |
    | Median abs. error % | {float(_n["median_abs_error_pct"]) * 100:.2f}% | {float(_a["median_abs_error_pct"]) * 100:.2f}% |
    | Rows | {int(_n["n"]):,} | {int(_a["n"]):,} |

    Mean absolute error in £ (national): £{float(_n["mean_abs_error_gbp"]):,.0f}
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _bins = pd.read_csv(
        mo.notebook_location() / "public" / "holdout_2025_error_bins.csv"
    )
    _fig, _ax = plt.subplots(figsize=(8, 3.5))

    for _model, _color, _label in (
        ("national", palette[0], "National"),
        ("area", palette[2], "Outward area"),
    ):
        _sub = _bins[_bins["model"] == _model].sort_values("bin_idx")
        _n = float(_sub["cnt"].sum())
        _dens = _sub["cnt"].values / _n
        _ax.bar(
            _sub["bin_idx"] + 0.5,
            _dens,
            width=1.0,
            alpha=0.55,
            color=_color,
            label=f"{_label} (n={int(_n):,})",
        )

    _ax.set_xlabel("Absolute error % (1% bins)")
    _ax.set_ylabel("Fraction of rows")
    _ax.set_title("2025 holdout: error distribution (full data, binned in SQL)")
    _ax.set_xlim(0, 100)
    _ax.grid(axis="y", alpha=0.3)
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend(frameon=False, loc="upper right")

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Historical backtest: national vs area

    Same methodology by calendar year: mean absolute **percentage** error over all scored transactions. **Area** uses local market means; **national** uses UK means.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _path = mo.notebook_location() / "public" / "yearly_accuracy_by_model.csv"
    _df = pd.read_csv(_path)

    _fig, _ax = plt.subplots(figsize=(10, 4))

    for _model, _color, _label in (
        ("national", palette[0], "National"),
        ("area", palette[2], "Outward area"),
    ):
        _sub = _df[_df["model"] == _model].sort_values("year")
        _ax.plot(
            _sub["year"],
            _sub["mean_absolute_error_percentage"] * 100,
            marker="o",
            markersize=3,
            color=_color,
            label=_label,
            linewidth=1.8,
        )

    _ax.set_title("Mean absolute percentage error by year (backtest)")
    _ax.set_xlabel("Sale year")
    _ax.set_ylabel("Mean |error| %")
    _ax.grid(axis="y", alpha=0.3)
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 2025: predicted vs actual (fixed sample)

    **8,000** national-model rows (deterministic sample from SQL) for the scatter; the right panel is the absolute error % on the same rows. Full distributions are in the binned chart above.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _df = pd.read_csv(mo.notebook_location() / "public" / "holdout_2025_sample.csv")
    _df = _df[_df["model"] == "national"]

    _err_pct = (
        (_df["predicted_price"] - _df["price_paid"]).abs() / _df["price_paid"] * 100
    )
    _hist_hi = min(100.0, float(_err_pct.quantile(0.99)) * 1.2)

    _fig, _axs = plt.subplots(1, 2, figsize=(11, 4))

    _axs[0].scatter(
        _df["price_paid"] / 1000,
        _df["predicted_price"] / 1000,
        s=4,
        alpha=0.25,
        c=palette[0],
        edgecolors="none",
    )
    _lim = max(_df["price_paid"].max(), _df["predicted_price"].max()) / 1000
    _axs[0].plot([0, _lim], [0, _lim], "k--", alpha=0.5, linewidth=1, label="y = x")
    _axs[0].set_title("2025: actual vs predicted (national sample)")
    _axs[0].set_xlabel("Price paid (£1k)")
    _axs[0].set_ylabel("Predicted (£1k)")
    _axs[0].set_xlim(0, _lim)
    _axs[0].set_ylim(0, _lim)
    _axs[0].set_aspect("equal", adjustable="box")
    _axs[0].spines["top"].set_visible(False)
    _axs[0].spines["right"].set_visible(False)
    _axs[0].legend(frameon=False)

    _axs[1].hist(
        _err_pct,
        bins=50,
        range=(0, _hist_hi),
        color=palette[2],
        alpha=0.85,
    )
    _axs[1].axvline(
        _err_pct.mean(),
        color="gray",
        linestyle="--",
        linewidth=1,
        label=f"Mean {_err_pct.mean():.1f}%",
    )
    _axs[1].set_title("Absolute error % (same sample)")
    _axs[1].set_xlabel("|Error| %")
    _axs[1].set_ylabel("Frequency")
    _axs[1].spines["top"].set_visible(False)
    _axs[1].spines["right"].set_visible(False)
    _axs[1].legend(frameon=False)

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Example: best vs worst national prediction (2025)

    - **Best (low error):** the 2025 sale (markers) sits near the model’s implied track: stable PMR history makes the extrapolation plausible.
    - **Worst (high error):** the 2025 sale is far from the predicted level—often a sharp change vs prior sales (extension, distress sale, or data quirks), which a PMR-only model cannot see.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _data_path = mo.notebook_location() / "public" / "national_year_avg.csv"
    _df = pd.read_csv(str(_data_path))

    _fig, _axs = plt.subplots(2, 1, figsize=(8, 4), sharex=True)

    for _i in range(2):
        _axs[_i].plot(
            _df["year"],
            _df["mean_price"] / 1000,
            marker=".",
            color=palette[0],
            label="National mean",
        )

    _df1 = pd.read_csv(
        mo.notebook_location() / "public" / "example_prediction_best.csv"
    )
    _axs[0].plot(
        _df1["year"],
        _df1["predicted_price"] / 1000,
        color=palette[1],
        label="Predicted",
    )
    _axs[0].plot(
        _df1["year"],
        _df1["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Sale",
    )
    _axs[0].set_ylabel("Price (£1k)")
    _axs[0].grid(axis="y")
    _axs[0].spines["top"].set_visible(False)
    _axs[0].spines["right"].set_visible(False)
    _axs[0].legend(
        loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.18)
    )

    _df2 = pd.read_csv(
        mo.notebook_location() / "public" / "example_prediction_worst.csv"
    )
    _axs[1].plot(
        _df2["year"],
        _df2["predicted_price"] / 1000,
        color=palette[1],
        label="Predicted",
    )
    _axs[1].plot(
        _df2["year"],
        _df2["price_paid"] / 1000,
        marker="X",
        linewidth=0,
        color=palette[2],
        label="Sale",
    )
    _axs[1].set_xlabel("Year")
    _axs[1].set_ylabel("Price (£1k)")
    _axs[1].grid(axis="y")
    _axs[1].spines["top"].set_visible(False)
    _axs[1].spines["right"].set_visible(False)

    _axs[0].text(1998, _axs[0].get_ylim()[1] * 0.82, "Best (2025)", fontweight="bold")
    _axs[1].text(1998, _axs[1].get_ylim()[1] * 0.82, "Worst (2025)", fontweight="bold")

    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo, pd):
    _m = pd.read_csv(mo.notebook_location() / "public" / "holdout_2025_metrics.csv")
    _pct_n = float(_m[_m["model"] == "national"]["mean_abs_error_pct"].iloc[0]) * 100
    _pct_a = float(_m[_m["model"] == "area"]["mean_abs_error_pct"].iloc[0]) * 100

    mo.md(
        f"""
    ## Summary

    This page shows a **DuckDB/SQL** pipeline on Land Registry data: **national** and **outward-area** price–market baselines, with PMR fit on **pre-2025** sales and **2025** used as a holdout.

    **2025 mean absolute error (national vs area):** {_pct_n:.2f}% vs {_pct_a:.2f}%.

    Limitations: no hedonic features, static PMR assumption, and area effects are coarse. Suitable as a **baseline** and a demonstration of **SQL analytics** plus simple **out-of-sample** checks—not a production valuation model.

    Repository: [github.com/bdevan5/property_prices](https://github.com/bdevan5/property_prices)
    """
    )
    return


if __name__ == "__main__":
    app.run()
