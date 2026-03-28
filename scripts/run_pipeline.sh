#!/usr/bin/env bash
# Run the full DuckDB pipeline from the repository root (paths in SQL are relative to cwd).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="${1:-data/property_transactions.db}"

cd "$ROOT"

duckdb_file() {
  echo "==> $1"
  duckdb "$DB" -f "$1"
}

duckdb_file sql/load.sql
duckdb_file sql/transform.sql
duckdb_file sql/clean.sql
duckdb_file sql/aggregate.sql
duckdb_file sql/predict_national.sql
duckdb_file sql/predict_area.sql
duckdb_file sql/calculate_accuracy.sql
duckdb_file sql/export_data_to_csv.sql

echo "Done: ${DB}"
