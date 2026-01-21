-- Replicates property_prices/generate_website_data.py using COPY statements

-- 1. Price Distribution    
-- WIP: not currently working....
-- COPY (
--     SELECT 
--         bin.key   AS bin_upper_edge,
--         bin.value AS frequency
--     FROM unnest(
--         select histogram(price_paid, equi_width_bins(0, 1000000, 100, false)) from transactions
--     ) AS bin(key, value)
--     ORDER BY bin_upper_edge;
-- ) TO 'web/public/price_distribution.csv' (FORMAT CSV, HEADER);


-- 2. Transaction Summary
-- Transposing metrics to match the Python script output structure (header=False)
COPY (
    SELECT 'n_transactions' AS metric, count(*)::VARCHAR AS value FROM transactions
    UNION ALL
    SELECT 'n_properties', count(distinct property_id)::VARCHAR FROM transactions
    UNION ALL
    SELECT 'mean_price', avg(price_paid)::VARCHAR FROM transactions
    UNION ALL
    SELECT 'std_price', stddev(price_paid)::VARCHAR FROM transactions
) TO 'web/public/transaction_summary.csv' (FORMAT CSV, HEADER FALSE);

-- 3. Average Yearly Sales
COPY (SELECT * FROM national_year_avg) TO 'web/public/avg_yearly_sales.csv' (FORMAT CSV, HEADER);

-- 4. HPI Average Yearly Sales
COPY (SELECT * FROM hpi_national_year_avg) TO 'web/public/hpi_avg_yearly_sales.csv' (FORMAT CSV, HEADER);

-- 5. HPI Accuracy
COPY (SELECT * FROM hpi_accuracy) TO 'web/public/hpi_accuracy.csv' (FORMAT CSV, HEADER);

-- 6. Best Predictions
-- COPY (
--     SELECT * FROM properties WHERE property_id IN (
--         SELECT property_id
--         FROM hpi_transaction_predictions
--         GROUP BY property_id
--         HAVING count(*) > 3
--         ORDER BY sum(abs(error)) ASC
--         LIMIT 6
--     )
-- ) TO 'web/public/best_predictions.csv' (FORMAT CSV, HEADER);

-- -- 7. Worst Predictions
-- -- Note: Replicating behavior from python script which used ASC (best) for worst_predictions as well.
-- COPY (
--     SELECT * FROM properties WHERE property_id IN (
--         SELECT property_id
--         FROM hpi_transaction_predictions
--         GROUP BY property_id
--         HAVING count(*) > 3
--         ORDER BY sum(abs(error)) ASC
--         LIMIT 6
--     )
-- ) TO 'web/public/worst_predictions.csv' (FORMAT CSV, HEADER);

-- -- 8. Predictions with Many Transactions
-- COPY (
--     SELECT * FROM properties WHERE property_id IN (
--         SELECT property_id
--         FROM transactions
--         GROUP BY property_id
--         HAVING count(*) > 7
--     )
-- ) TO 'web/public/predictions_with_many_transactions.csv' (FORMAT CSV, HEADER);
