-- ================================================================================================
--  Create and Populate Mapping Tables
-- ================================================================================================

-- Create dim_team_mapping table
CREATE TABLE IF NOT EXISTS dim_team_mapping (
    statsbomb_team_id INT PRIMARY KEY,
    dim_team_id INT,
    INDEX idx_dim_team (dim_team_id)
);

-- Create dim_match_mapping table
CREATE TABLE IF NOT EXISTS dim_match_mapping (
    statsbomb_match_id INT PRIMARY KEY,
    csv_match_id INT,
    INDEX idx_csv_match (csv_match_id)
);

-- Populate dim_team_mapping from unique teams in events
-- Use explicit StatsBomb ID to dim_team ID mapping (based on team names)
INSERT IGNORE INTO dim_team_mapping (statsbomb_team_id, dim_team_id)
VALUES
(1, 1),      -- Arsenal FC
(22, 2),     -- Aston Villa FC
(23, 3),     -- Chelsea FC
(24, 4),     -- Everton FC
(25, 14),    -- Crystal Palace FC
(26, 5),     -- Fulham FC
(27, 23),    -- Ipswich Town FC
(28, 21),    -- Leicester City FC
(29, 6),     -- Liverpool FC
(30, -1),    -- (International team - not in EPL)
(31, -1),    -- (International team - not in EPL)
(32, 9),     -- Newcastle United FC
(33, -1),    -- (International team - not in EPL)
(34, 13),    -- Nottingham Forest FC
(35, 22),    -- Southampton FC
(36, 10),    -- Tottenham Hotspur FC
(37, 19),    -- West Ham United FC
(38, 11),    -- Wolverhampton Wanderers FC
(39, -1),    -- (International team - not in EPL)
(40, 17),    -- Brighton & Hove Albion FC
(41, -1),    -- (International team - not in EPL)
(56, -1),    -- (International team - not in EPL)
(59, -1),    -- (International team - not in EPL)
(90, 18);    -- Brentford FC

-- Handle any remaining unmapped teams (use sentinel value -1)
INSERT IGNORE INTO dim_team_mapping (statsbomb_team_id, dim_team_id)
SELECT DISTINCT 
    se.team_id,
    -1
FROM stg_events_raw se
LEFT JOIN dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id
WHERE dtm.statsbomb_team_id IS NULL
  AND se.team_id > 0;

-- Verify team mapping
SELECT 'Team Mapping Results:' as status;
SELECT COUNT(*) as total_mappings FROM dim_team_mapping;
SELECT COUNT(DISTINCT statsbomb_team_id) as unique_statsbomb_teams FROM dim_team_mapping;

-- Populate dim_match_mapping: Sequential mapping (first 380 CSV matches to StatsBomb IDs)
-- We have 380 StatsBomb matches and need to map them to 380 CSV matches
INSERT IGNORE INTO dim_match_mapping (statsbomb_match_id, csv_match_id)
SELECT 
    smatch.statsbomb_match_id,
    ROW_NUMBER() OVER (ORDER BY smatch.statsbomb_match_id) as csv_match_id
FROM (
    SELECT DISTINCT statsbomb_match_id 
    FROM stg_events_raw 
    WHERE statsbomb_match_id > 0
    ORDER BY statsbomb_match_id
) smatch;

-- Verify match mapping
SELECT 'Match Mapping Results:' as status;
SELECT COUNT(*) as total_match_mappings FROM dim_match_mapping;
SELECT COUNT(DISTINCT statsbomb_match_id) as unique_statsbomb_matches FROM dim_match_mapping;
