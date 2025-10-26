-- Step 3 (Final): Load events into fact_match_events  
-- Using sentinel values: player_id=6808 (UNKNOWN), team_id=-1 for unknowns
INSERT INTO fact_match_events (
        match_id,
        event_type,
        player_id,
        team_id,
        minute,
        extra_time
)
SELECT  dmm.csv_match_id,
        se.type,
        COALESCE(dp.player_id, 6808),
        COALESCE(dtm.dim_team_id, -1),
        se.minute,
        CASE WHEN se.statsbomb_period = 2 AND se.minute > 45 THEN se.minute - 45
             WHEN se.statsbomb_period >= 3 THEN se.minute
             ELSE 0 END
FROM    stg_events_raw se
JOIN    dim_match_mapping dmm ON dmm.statsbomb_match_id = se.statsbomb_match_id
LEFT JOIN dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id
LEFT JOIN dim_player dp ON dp.player_name = se.player_name
WHERE   se.status = 'LOADED'
  AND   se.minute BETWEEN 0 AND 120;

-- Verify results
SELECT COUNT(*) AS total_events,
       COUNT(DISTINCT match_id) AS matches_with_events,
       COUNT(DISTINCT player_id) AS players_seen,
       SUM(CASE WHEN player_id = 6808 THEN 1 ELSE 0 END) AS unknown_player_events
FROM   fact_match_events;
