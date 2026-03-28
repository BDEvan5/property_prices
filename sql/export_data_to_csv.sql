-- Minimal CSVs for the Marimo site (run after calculate_accuracy.sql).
-- Full 2025 prediction rows are not exported—use metrics, binned errors, and fixed-size samples.

-- --- Raw / exploratory ---
COPY (
    WITH cleaned AS (
        SELECT
            count(*) AS count_cleaned,
            year(deed_date) AS transaction_year
        FROM transactions_cleaned
        GROUP BY year(deed_date)
    ),
    all_transactions AS (
        SELECT
            count(*) AS count_all,
            year(deed_date) AS transaction_year
        FROM transactions
        GROUP BY year(deed_date)
    )
    SELECT
        c.transaction_year,
        a.count_all,
        c.count_cleaned
    FROM cleaned AS c
    INNER JOIN all_transactions AS a USING (transaction_year)
    ORDER BY c.transaction_year
) TO 'web/public/transactions_cleaned_by_year.csv' (FORMAT CSV, HEADER);

COPY (
    WITH stats AS (
        SELECT histogram(price_paid, equi_width_bins(0, 1000000, 100, false)) AS hist_map
        FROM transactions
    )
    SELECT
        entry.key AS bin_end,
        entry.value AS count
    FROM (
        SELECT unnest(map_entries(hist_map)) AS entry
        FROM stats
    )
    WHERE bin_end <= 1000000
    ORDER BY bin_end
) TO 'web/public/price_distribution.csv' (FORMAT CSV, HEADER);

COPY (
    SELECT 'n_transactions' AS metric, count(*)::VARCHAR AS value FROM transactions
    UNION ALL
    SELECT 'n_properties', count(DISTINCT property_id)::VARCHAR FROM transactions
    UNION ALL
    SELECT 'mean_price', avg(price_paid)::VARCHAR FROM transactions
    UNION ALL
    SELECT 'std_price', stddev_samp(price_paid)::VARCHAR FROM transactions
) TO 'web/public/transaction_summary.csv' (FORMAT CSV, HEADER FALSE);

COPY (SELECT * FROM national_year_avg) TO 'web/public/national_year_avg.csv' (FORMAT CSV, HEADER);

COPY (
    SELECT 'national' AS model, * FROM yearly_accuracy_national
    UNION ALL
    SELECT 'area' AS model, * FROM yearly_accuracy_area
) TO 'web/public/yearly_accuracy_by_model.csv' (FORMAT CSV, HEADER);

-- --- 2025 holdout (compact): metrics, 1%-wide error bins, fixed samples ---
COPY (
    SELECT
        'national'::VARCHAR AS model,
        count(*)::BIGINT AS n,
        avg(abs((price_paid - predicted_price) / price_paid)) AS mean_abs_error_pct,
        median(abs((price_paid - predicted_price) / price_paid)) AS median_abs_error_pct,
        avg(abs(price_paid - predicted_price)) AS mean_abs_error_gbp
    FROM predictions_national
    WHERE year = 2025
    UNION ALL
    SELECT
        'area'::VARCHAR AS model,
        count(*)::BIGINT AS n,
        avg(abs((price_paid - predicted_price) / price_paid)) AS mean_abs_error_pct,
        median(abs((price_paid - predicted_price) / price_paid)) AS median_abs_error_pct,
        avg(abs(price_paid - predicted_price)) AS mean_abs_error_gbp
    FROM predictions_area
    WHERE year = 2025
) TO 'web/public/holdout_2025_metrics.csv' (FORMAT CSV, HEADER);

COPY (
    SELECT
        'national'::VARCHAR AS model,
        cast(
            floor(least(abs((price_paid - predicted_price) / price_paid), 1.0) * 100) AS integer
        ) AS bin_idx,
        count(*)::BIGINT AS cnt
    FROM predictions_national
    WHERE year = 2025
    GROUP BY
        cast(floor(least(abs((price_paid - predicted_price) / price_paid), 1.0) * 100) AS integer)
    UNION ALL
    SELECT
        'area'::VARCHAR AS model,
        cast(
            floor(least(abs((price_paid - predicted_price) / price_paid), 1.0) * 100) AS integer
        ) AS bin_idx,
        count(*)::BIGINT AS cnt
    FROM predictions_area
    WHERE year = 2025
    GROUP BY
        cast(floor(least(abs((price_paid - predicted_price) / price_paid), 1.0) * 100) AS integer)
) TO 'web/public/holdout_2025_error_bins.csv' (FORMAT CSV, HEADER);

COPY (
    (
        SELECT
            'national'::VARCHAR AS model,
            price_paid,
            predicted_price
        FROM predictions_national
        WHERE year = 2025
        ORDER BY unique_id
        LIMIT 8000
    )
    UNION ALL
    (
        SELECT
            'area'::VARCHAR AS model,
            price_paid,
            predicted_price
        FROM predictions_area
        WHERE year = 2025
        ORDER BY unique_id
        LIMIT 8000
    )
) TO 'web/public/holdout_2025_sample.csv' (FORMAT CSV, HEADER);

-- --- Example series (same property selection as before) ---
COPY (
    WITH example_properties AS (
        SELECT property_id
        FROM transactions_cleaned
        GROUP BY property_id
        HAVING count(*) > 5
        ORDER BY count(*) DESC
        LIMIT 1
    )
    SELECT
        year,
        predicted_price,
        price_paid
    FROM predictions_national
    WHERE property_id IN (SELECT property_id FROM example_properties)
    ORDER BY year
) TO 'web/public/example_prediction.csv' (FORMAT CSV, HEADER);

COPY (
    WITH example_properties AS (
        SELECT property_id
        FROM transactions_cleaned
        GROUP BY property_id
        HAVING count(*) > 5
        ORDER BY count(*) DESC
        LIMIT 1
    ),
    prop_area AS (
        SELECT pc.area AS area
        FROM properties AS pr
        INNER JOIN postcodes AS pc ON pr.postcode = pc.postcode
        WHERE pr.property_id IN (SELECT property_id FROM example_properties)
        LIMIT 1
    )
    SELECT
        a.year,
        a.mean_price,
        a.area
    FROM area_year_avg AS a
    WHERE a.area = (SELECT area FROM prop_area)
    ORDER BY a.year
) TO 'web/public/example_area_year_avg.csv' (FORMAT CSV, HEADER);

COPY (
    WITH example_properties AS (
        SELECT property_id
        FROM transactions_cleaned
        GROUP BY property_id
        HAVING count(*) > 5 AND max(year(deed_date)) = 2025
    ),
    best_properties AS (
        SELECT p.property_id
        FROM predictions_national AS p
        WHERE p.year = 2025
            AND p.property_id IN (SELECT property_id FROM example_properties)
        ORDER BY abs((p.price_paid - p.predicted_price) / p.price_paid) ASC
        LIMIT 1
    )
    SELECT
        p.year,
        p.predicted_price,
        p.price_paid
    FROM predictions_national AS p
    WHERE p.property_id IN (SELECT property_id FROM best_properties)
    ORDER BY p.year
) TO 'web/public/example_prediction_best.csv' (FORMAT CSV, HEADER);

COPY (
    WITH example_properties AS (
        SELECT property_id
        FROM transactions_cleaned
        GROUP BY property_id
        HAVING count(*) > 5 AND max(year(deed_date)) = 2025
    ),
    worst_properties AS (
        SELECT p.property_id
        FROM predictions_national AS p
        WHERE p.year = 2025
            AND p.property_id IN (SELECT property_id FROM example_properties)
        ORDER BY abs((p.price_paid - p.predicted_price) / p.price_paid) DESC
        LIMIT 1
    )
    SELECT
        p.year,
        p.predicted_price,
        p.price_paid
    FROM predictions_national AS p
    WHERE p.property_id IN (SELECT property_id FROM worst_properties)
    ORDER BY p.year
) TO 'web/public/example_prediction_worst.csv' (FORMAT CSV, HEADER);
