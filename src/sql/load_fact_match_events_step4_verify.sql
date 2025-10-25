-- Step 4: Comprehensive verification
SELECT COUNT(*) AS total_events,
       COUNT(DISTINCT match_id) AS matches_with_events,
       COUNT(DISTINCT player_id) AS players_seen,
       COUNT(DISTINCT team_id) AS teams_involved,
       MIN(minute) AS min_minute,
       MAX(minute) AS max_minute
FROM   fact_match_events;

-- Event type distribution
SELECT event_type, COUNT(*) AS event_count 
FROM fact_match_events 
GROUP BY event_type 
ORDER BY event_count DESC 
LIMIT 15;

-- Verify FK integrity
SELECT 'fact_match' AS table_name, COUNT(*) FROM fact_match
UNION ALL
SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
UNION ALL
SELECT 'dim_player', COUNT(*) FROM dim_player
UNION ALL
SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL
SELECT 'dim_match_mapping', COUNT(*) FROM dim_match_mapping;
