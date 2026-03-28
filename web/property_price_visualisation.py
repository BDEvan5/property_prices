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

    **What this is:** [HM Land Registry](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads) Price Paid records ingested into **DuckDB**, with **national** and **outward-area** baselines implemented in **SQL** and evaluated in **Python** (this page).

    **Evaluation:** Each property’s price–market ratio (PMR) is estimated from sales **before 2025**; **2025** transactions are held out so reported errors are genuinely out-of-sample.

    **Code:** [github.com/bdevan5/property_prices](https://github.com/bdevan5/property_prices)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Data at a glance

    CSVs are loaded into DuckDB, normalised into `properties` and `transactions`, and joined to a postcode **area** table for regional aggregates. The figure and summary statistics describe the modelling set.
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

    **Holdout:** 2025 sales are predicted using data only through **2024**—PMRs and aggregates in the SQL pipeline are fit on **pre-2025** transactions.

    **Filters** (applied to transactions):
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

    The baselines assume a property’s **price–market ratio** (PMR)—price divided by the prior year’s market mean—is stable over time. That is a deliberate simplification: there is no hedonic detail (condition, extensions, micro-location).

    **Two SQL baselines:**
    1. **National:** prior-year **UK** mean × mean PMR (from prior sales).
    2. **Outward area:** prior-year mean for the postcode **area** (e.g. `SW`) × mean PMR.

    **Pipeline:** (1) yearly aggregates, (2) per-transaction PMR and per-property average PMR from pre-2025 sales, (3) multiply by the relevant prior-year mean for each sale year (including 2025 holdout).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 1. National market context

    Long-run UK price levels and dispersion for the cleaned transaction set.
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

    One property with many sales in the cleaned set. **Top row:** UK mean vs outward **area** mean (e.g. `SW`) against sale prices. **Bottom row:** PMR = price ÷ that year’s mean, with the horizontal dashed line showing **mean PMR** used for forecasts. The area baseline tracks local market level; the national baseline smooths geography.
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

    For each 2025 sale, **predicted price = prior-year mean × fitted mean PMR**. The **national** baseline multiplies each property’s PMR by the **{2024}** UK mean (£{_m2024:,.0f}); the **area** baseline uses the prior-year mean for that property’s outward area.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Out-of-sample error (2025)

    Error is mean absolute **percentage** error: |actual − predicted| / actual. The table compares **national** and **outward-area** baselines on the same 2025 sales (restricted to rows where the area model applies).
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
    | Mean absolute error % | {float(_n["mean_abs_error_pct"]) * 100:.2f}% | {float(_a["mean_abs_error_pct"]) * 100:.2f}% |
    | Median absolute error % | {float(_n["median_abs_error_pct"]) * 100:.2f}% | {float(_a["median_abs_error_pct"]) * 100:.2f}% |
    | Transactions scored | {int(_n["n"]):,} | {int(_a["n"]):,} |

    Mean absolute error in £ (national baseline): £{float(_n["mean_abs_error_gbp"]):,.0f}
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Rolling backtest by year

    The same scoring rule applied historically: for each year, mean absolute **percentage** error over transactions scored that year. **Area** uses local prior-year means; **national** uses the UK prior-year mean—so you can see how the gap between baselines evolves over time.
    """)
    return


@app.cell
def _(mo, palette, pd, plt):
    _path = mo.notebook_location() / "public" / "yearly_accuracy_by_model.csv"
    _df = pd.read_csv(_path)

    _fig, _ax = plt.subplots(figsize=(10, 4.9))

    for _model, _color, _label in (
        ("national", palette[0], "National"),
        ("area", palette[2], "Outward area"),
    ):
        _sub = _df[_df["model"] == _model].sort_values("year")
        _ax.plot(
            _sub["year"],
            _sub["mean_absolute_error_percentage"] * 100,
            marker="o",
            markersize=4,
            color=_color,
            label=_label,
            linewidth=2,
        )

    _ax.set_title(
        "Mean absolute percentage error by year (backtest)",
        fontsize=12,
        pad=14,
    )
    _ax.set_xlabel("Sale year")
    _ax.set_ylabel("Mean absolute error (%)")
    _ax.grid(axis="y", alpha=0.35, linestyle="-", linewidth=0.8)
    _ax.set_axisbelow(True)
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.legend(
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        frameon=True,
        framealpha=0.98,
        facecolor="white",
        edgecolor="0.88",
        fontsize=10,
        columnspacing=2.0,
        handletextpad=0.9,
        borderpad=0.9,
    )
    _fig.text(
        0.5,
        0.06,
        "Mean |actual − predicted| / actual by sale year; each year scored using models\n"
        "fit only on data from earlier years.",
        ha="center",
        va="bottom",
        fontsize=9,
        color="0.38",
        linespacing=1.35,
    )
    _fig.subplots_adjust(left=0.09, right=0.98, top=0.90, bottom=0.34)
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### 2025: predicted vs actual (sample)

    **8,000** transactions from the national baseline (deterministic SQL sample): **left**, actual vs predicted price; **right**, the distribution of absolute percentage error on the same rows.
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

    Two properties illustrate what the baseline can and cannot capture.

    - **Best (low error):** the 2025 sale aligns with the extrapolated track—stable PMR history makes the forecast plausible.
    - **Worst (high error):** the 2025 sale sits far from the prediction—often a sharp break vs prior sales (e.g. renovation, distress, or data issues), which a PMR-only model cannot infer.
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

    End-to-end **DuckDB** analytics on Land Registry data: **SQL** aggregates and baselines (**national** vs **outward-area** PMRs), **Python** for evaluation, and a clear **pre-2025 / 2025** holdout split.

    **2025 mean absolute percentage error** (national vs area): **{_pct_n:.2f}%** vs **{_pct_a:.2f}%**.

    **Scope:** This is a deliberate baseline—no hedonic features, a static PMR assumption, and coarse geography. It demonstrates **reproducible SQL pipelines**, **honest out-of-sample metrics**, and how far simple structure can go before you need richer modelling.

    **Repository:** [github.com/bdevan5/property_prices](https://github.com/bdevan5/property_prices)
    """
    )
    return


if __name__ == "__main__":
    app.run()
