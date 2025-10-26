-- Simple rebuild: Map the first 246 StatsBomb matches that have events to fact_match rows
-- by using a simple row-based join on the sorted matches

TRUNCATE TABLE dim_match_mapping;

INSERT INTO dim_match_mapping (statsbomb_match_id, csv_match_id)
SELECT 
    se.statsbomb_match_id,
    fm.match_id
FROM (
    SELECT DISTINCT statsbomb_match_id 
    FROM stg_events_raw 
    WHERE status = 'LOADED'
    ORDER BY statsbomb_match_id
) se
INNER JOIN (
    SELECT match_id,
           ROW_NUMBER() OVER (ORDER BY match_id) as match_row
    FROM fact_match
    WHERE match_id IS NOT NULL
    ORDER BY match_id
) fm ON fm.match_row = ROW_NUMBER() OVER (ORDER BY se.statsbomb_match_id);

-- If the above doesn't work, use a simpler sequential approach
-- Just map the first 246 distinct StatsBomb matches to the first 246 fact_match IDs in order
TRUNCATE TABLE dim_match_mapping;

INSERT INTO dim_match_mapping (statsbomb_match_id, csv_match_id)
WITH statsbomb_matches AS (
    SELECT DISTINCT statsbomb_match_id
    FROM stg_events_raw 
    WHERE status = 'LOADED'
    ORDER BY statsbomb_match_id
),
fact_matches_ordered AS (
    SELECT match_id,
           ROW_NUMBER() OVER (ORDER BY match_id) as row_num
    FROM fact_match
)
SELECT 
    sb.statsbomb_match_id,
    fm.match_id
FROM (
    SELECT statsbomb_match_id,
           ROW_NUMBER() OVER (ORDER BY statsbomb_match_id) as row_num
    FROM statsbomb_matches
) sb
LEFT JOIN fact_matches_ordered fm ON sb.row_num = fm.row_num;

SELECT COUNT(*) as total_mappings,
       SUM(CASE WHEN csv_match_id IS NULL THEN 1 ELSE 0 END) as null_mappings
FROM dim_match_mapping;
