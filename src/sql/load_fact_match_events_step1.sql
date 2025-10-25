-- Step 1: Create temporary helper table
-- Collapse 1.3M events → 1 row per (StatsBomb match, dim_team)
CREATE TEMPORARY TABLE tmp_epl_team_per_match AS
SELECT  se.statsbomb_match_id,
        dtm.dim_team_id
FROM    stg_events_raw se
JOIN    dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id
GROUP BY se.statsbomb_match_id, dtm.dim_team_id;

CREATE INDEX idx_tmp_match ON tmp_epl_team_per_match(statsbomb_match_id);

-- Verify results
SELECT COUNT(*) AS tmp_table_rows FROM tmp_epl_team_per_match;
SELECT COUNT(DISTINCT statsbomb_match_id) AS unique_matches,
       COUNT(DISTINCT dim_team_id) AS unique_teams
FROM tmp_epl_team_per_match;
