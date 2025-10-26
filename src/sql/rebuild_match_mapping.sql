-- Rebuild dim_match_mapping after fact_match is loaded
-- This maps StatsBomb match IDs to the actual fact_match.match_id values

-- Clear existing mapping
TRUNCATE TABLE dim_match_mapping;

-- Recreate mapping by joining stg_events_raw to fact_match on date
-- This is more robust than using sequence numbers
INSERT INTO dim_match_mapping (statsbomb_match_id, csv_match_id)
SELECT DISTINCT 
    se.statsbomb_match_id,
    fm.match_id
FROM stg_events_raw se
INNER JOIN fact_match fm ON (
    fm.date_id = CAST(CONCAT(
        YEAR(se.match_date), 
        LPAD(MONTH(se.match_date), 2, '0'), 
        LPAD(DAY(se.match_date), 2, '0')
    ) AS INT)
    AND fm.season_id = COALESCE(
        (SELECT season_id FROM dim_season 
         WHERE YEAR(se.match_date) >= YEAR(STR_TO_DATE(season_name, '%Y/%y'))
         ORDER BY season_id DESC LIMIT 1),
        -1
    )
)
WHERE se.status = 'LOADED'
GROUP BY se.statsbomb_match_id, fm.match_id;

-- Verify results
SELECT COUNT(*) AS total_match_mappings,
       COUNT(DISTINCT statsbomb_match_id) AS unique_statsbomb_matches,
       COUNT(DISTINCT csv_match_id) AS unique_csv_matches
FROM dim_match_mapping;

SELECT 'Rebuild complete' AS status;
