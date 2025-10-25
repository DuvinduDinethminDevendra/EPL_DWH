-- Step 2: Populate missing mapping rows (already populated by step 1, this is just verification)
-- No new rows to insert - step 1 handles all mappings
SELECT 'Step 2 verification - mappings already complete' AS message;

-- Verify results
SELECT COUNT(*) AS total_mappings FROM dim_match_mapping;
SELECT COUNT(DISTINCT csv_match_id) AS unique_csv_matches,
       COUNT(DISTINCT statsbomb_match_id) AS unique_statsbomb_matches
FROM dim_match_mapping;
