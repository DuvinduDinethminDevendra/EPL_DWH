-- Step: Load fact_player_stats from staging
-- For PoC: Associate all player stats with the first match per team per season

INSERT INTO fact_player_stats (match_id, player_id, team_id, minutes_played, goals, assists, yellow_cards, red_cards, shots)
SELECT
    (SELECT MIN(m.match_id) FROM fact_match m WHERE m.season_id = ds.season_id AND (m.home_team_id = dt.team_id OR m.away_team_id = dt.team_id)) AS match_id,
    COALESCE(dp.player_id, 6808) AS player_id,  -- 6808 = UNKNOWN player
    COALESCE(dt.team_id, -1) AS team_id,        -- -1 = UNKNOWN team
    s.minutes_played,
    s.goals,
    s.assists,
    s.yellow_cards,
    s.red_cards,
    s.shots
FROM stg_player_stats_fbref s
LEFT JOIN dim_player dp ON dp.player_name = s.player_name
LEFT JOIN dim_team dt ON dt.team_name = s.team_name
LEFT JOIN dim_season ds ON ds.season_name LIKE CONCAT('%', LEFT(s.season_label, 4), '%')
WHERE s.player_name IS NOT NULL 
  AND s.team_name IS NOT NULL
  AND (SELECT MIN(m.match_id) FROM fact_match m WHERE m.season_id = ds.season_id AND (m.home_team_id = dt.team_id OR m.away_team_id = dt.team_id)) IS NOT NULL
ON DUPLICATE KEY UPDATE
    minutes_played = VALUES(minutes_played),
    goals = VALUES(goals),
    assists = VALUES(assists),
    yellow_cards = VALUES(yellow_cards),
    red_cards = VALUES(red_cards),
    shots = VALUES(shots);

-- Verify results
SELECT 
    COUNT(*) AS total_player_stats,
    COUNT(DISTINCT player_id) AS unique_players,
    COUNT(DISTINCT team_id) AS unique_teams,
    COALESCE(SUM(goals), 0) AS total_goals,
    COALESCE(SUM(assists), 0) AS total_assists
FROM fact_player_stats;
