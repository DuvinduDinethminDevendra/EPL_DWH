-- Final DWH Row Count Verification
SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dim_date
UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL SELECT 'dim_season', COUNT(*) FROM dim_season
UNION ALL SELECT 'dim_player', COUNT(*) FROM dim_player
UNION ALL SELECT 'dim_referee', COUNT(*) FROM dim_referee
UNION ALL SELECT 'dim_stadium', COUNT(*) FROM dim_stadium
UNION ALL SELECT 'dim_match_mapping', COUNT(*) FROM dim_match_mapping
UNION ALL SELECT 'dim_team_mapping', COUNT(*) FROM dim_team_mapping
UNION ALL SELECT 'fact_match', COUNT(*) FROM fact_match
UNION ALL SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
UNION ALL SELECT 'fact_player_stats', COUNT(*) FROM fact_player_stats
UNION ALL SELECT 'stg_events_raw', COUNT(*) FROM stg_events_raw
UNION ALL SELECT 'stg_e0_match_raw', COUNT(*) FROM stg_e0_match_raw
UNION ALL SELECT 'stg_team_raw', COUNT(*) FROM stg_team_raw
UNION ALL SELECT 'stg_player_raw', COUNT(*) FROM stg_player_raw
UNION ALL SELECT 'stg_referee_raw', COUNT(*) FROM stg_referee_raw
UNION ALL SELECT 'stg_player_stats_fbref', COUNT(*) FROM stg_player_stats_fbref
UNION ALL SELECT 'ETL_Log', COUNT(*) FROM ETL_Log
UNION ALL SELECT 'ETL_File_Manifest', COUNT(*) FROM ETL_File_Manifest
UNION ALL SELECT 'ETL_Api_Manifest', COUNT(*) FROM ETL_Api_Manifest
UNION ALL SELECT 'ETL_JSON_Manifest', COUNT(*) FROM ETL_JSON_Manifest
ORDER BY table_name;
