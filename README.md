# Property price modelling (UK Land Registry)

**UK house prices: DuckDB SQL pipeline plus simple price–market-style predictions; national and outward-postcode-area baselines compared.**

This repository loads [HM Land Registry price-paid data](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads), builds a normalised schema in DuckDB, and evaluates two baselines: a **national** mean series and an **outward-area** (e.g. `SW`, `M`) mean series. Each baseline multiplies a property’s historical price–market ratio by the prior year’s aggregate mean to form forward-year predictions, then reports error metrics by year.

**Live demo:** [GitHub Pages](https://bdevan5.github.io/property_prices/) (Marimo export of `web/property_price_visualisation.py`).

## SQL pipeline

Run from the repository root so paths resolve (`data/…`, `web/public/…`).

**One command:**

```bash
./scripts/run_pipeline.sh
```

Optional database path (default `data/properties.db`):

```bash
./scripts/run_pipeline.sh path/to/my.db
```

**Step by step:**

```bash
duckdb data/properties.db -f sql/load.sql
duckdb data/properties.db -f sql/transform.sql
duckdb data/properties.db -f sql/clean.sql
duckdb data/properties.db -f sql/aggregate.sql
duckdb data/properties.db -f sql/predict_national.sql
duckdb data/properties.db -f sql/predict_area.sql
duckdb data/properties.db -f sql/calculate_accuracy.sql
duckdb data/properties.db -f sql/export_data_to_csv.sql
```

| Script | Purpose |
|--------|---------|
| `load.sql` | `raw_data` **view** over the CSV (no extra table copy) |
| `transform.sql` | `properties`, `transactions`, `postcodes` |
| `clean.sql` | `transactions_cleaned` / `properties_cleaned` |
| `aggregate.sql` | `national_year_avg`, `area_year_avg`, district / sector / postcode aggregates |
| `predict_national.sql` | `transaction_pmr_national`, `property_pmr_national`, **`predictions_national`** (one row per modelled transaction) |
| `predict_area.sql` | `transaction_pmr_area`, `property_pmr_area`, **`predictions_area`** |
| `calculate_accuracy.sql` | `yearly_accuracy_national`, `yearly_accuracy_area`; view **`predictions`** = national (compat) |
| `export_data_to_csv.sql` | Small CSVs for the Marimo site (no full 2025 row dumps—metrics, 1% error bins, 8k-row samples, examples) |

### Schema notes

- **`raw_data`**: view on `read_csv` so Land Registry files are not stored twice; downstream tables are `properties` and `transactions`.
- **`postcodes`**: one row per distinct postcode (regex-derived area fields), materialised as a table in `transform.sql`.
- **Predictions:** `predictions_national` and `predictions_area` share the same columns: `unique_id`, `property_id`, `deed_date`, `year`, `price_paid`, `predicted_price` — only **actual** cleaned transactions get a row. Property mean PMR is fit on **transactions before 2025** only; later years (including 2025) are still scored using that PMR.
- **National vs area scripts:** each file only creates objects with the `_national` or `_area` suffix.
- **Exports:** **`export_data_to_csv.sql`** writes only what the notebook needs (e.g. `holdout_2025_metrics.csv`, `holdout_2025_error_bins.csv`, `holdout_2025_sample.csv`). Run the pipeline before `marimo export` so `web/public/` is populated; large prediction CSVs are not committed.

## Marimo site (local)

```bash
uv sync
uv run marimo export html web/property_price_visualisation.py -o web/output/index.html --no-include-code -f
```

GitHub Actions on `master` runs `uv sync` and the same export, then deploys `web/output` to Pages.

## Data

Source: HM Land Registry. Set the CSV path in `sql/load.sql` under `data/raw_land_registry/` (or another path). Large files are read from disk when queries touch `raw_data` or the derived tables.
