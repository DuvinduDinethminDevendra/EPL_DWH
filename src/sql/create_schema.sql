-- D:\myPortfolioProject\EPL_DWH\src\sql\create_schema.sql
-- Canonical create_schema.sql (cleaned and idempotent)
-- Creates database, tables, sentinel rows, and initial data for epl_dw

CREATE DATABASE IF NOT EXISTS epl_dw
    DEFAULT CHARACTER SET = 'utf8mb4'
    DEFAULT COLLATE = 'utf8mb4_0900_ai_ci';
USE epl_dw;

-- Temporarily disable FK checks for initial drops
SET FOREIGN_KEY_CHECKS = 0;

-- Drop in safe order (idempotent)
DROP TABLE IF EXISTS fact_player_stats;
DROP TABLE IF EXISTS fact_match_events;
DROP TABLE IF EXISTS fact_match;

DROP TABLE IF EXISTS dim_referee;
DROP TABLE IF EXISTS dim_stadium;
DROP TABLE IF EXISTS dim_player;
DROP TABLE IF EXISTS dim_team;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_season;

DROP TABLE IF EXISTS ETL_Log;
DROP TABLE IF EXISTS ETL_File_Manifest;
DROP TABLE IF EXISTS ETL_Api_Manifest;
DROP TABLE IF EXISTS ETL_Excel_Manifest;

DROP TABLE IF EXISTS staging_matches;
DROP TABLE IF EXISTS staging_players;
DROP TABLE IF EXISTS staging_teams;
DROP TABLE IF EXISTS staging_referees;
DROP TABLE IF EXISTS staging_dates;
DROP TABLE IF EXISTS stg_e0_match_raw;
DROP TABLE IF EXISTS stg_team_raw;
DROP TABLE IF EXISTS stg_referee_raw;
DROP TABLE IF EXISTS stg_events_raw;

SET FOREIGN_KEY_CHECKS = 1;

-- CONTROL TABLES
CREATE TABLE IF NOT EXISTS ETL_Log (
    log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    phase_step VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    rows_processed INT,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ETL_File_Manifest (
    file_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    league_div VARCHAR(5) NOT NULL,
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL,
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ETL_Api_Manifest (
    api_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    api_name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    season INT,
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL,
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_api_call (api_name, endpoint, season)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ETL_Excel_Manifest (
    excel_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    file_path VARCHAR(255) NOT NULL,
    sheet_name VARCHAR(255),
    data_type VARCHAR(100),
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL,
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_name (file_name),
    INDEX idx_file_path (file_path),
    INDEX idx_data_type (data_type),
    INDEX idx_status (status),
    INDEX idx_load_start_time (load_start_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ETL_Events_Manifest (
    event_manifest_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    statsbomb_match_id VARCHAR(50) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255),
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_statsbomb_match_id (statsbomb_match_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- STAGING
CREATE TABLE IF NOT EXISTS stg_e0_match_raw (
    match_source_key VARCHAR(255) NOT NULL PRIMARY KEY,
    `Div` VARCHAR(5),
    `Date` DATE,
    `Time` TIME,
    season VARCHAR(20),
    HomeTeam VARCHAR(255),
    AwayTeam VARCHAR(255),
    FTHG INT,
    FTAG INT,
    FTR CHAR(1),
    HTHG INT,
    HTAG INT,
    HTR CHAR(1),
    Referee VARCHAR(255),
    HS INT,
    `AS` INT,
    HST INT,
    AST INT,
    HF INT,
    AF INT,
    HC INT,
    AC INT,
    HY INT,
    AY INT,
    HR INT,
    AR INT,
    load_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS stg_team_raw (
    api_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    api_name VARCHAR(255) DEFAULT 'FootballData.org',
    endpoint VARCHAR(255),
    team_id INT,
    load_start_time DATETIME,
    load_end_time DATETIME,
    status VARCHAR(20),
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Raw data fields
    name VARCHAR(255),
    shortName VARCHAR(255),
    tla VARCHAR(10),
    crest VARCHAR(512),
    address VARCHAR(255),
    website VARCHAR(255),
    founded INT,
    clubColors VARCHAR(100),
    venue VARCHAR(255),
    runningCompetitions JSON,
    squad JSON,
    staff JSON,
    lastUpdated DATETIME,
    area_id INT,
    area_name VARCHAR(255),
    area_code VARCHAR(10),
    area_flag VARCHAR(512),
    coach_id INT,
    coach_firstName VARCHAR(100),
    coach_lastName VARCHAR(100),
    coach_name VARCHAR(255),
    coach_dateOfBirth DATE,
    coach_nationality VARCHAR(100),
    coach_contract_start DATE,
    coach_contract_until DATE,
    -- Indexes for performance and audit trail
    INDEX idx_api_name (api_name),
    INDEX idx_endpoint (endpoint),
    INDEX idx_team_id (team_id),
    INDEX idx_status (status),
    INDEX idx_load_start_time (load_start_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS stg_player_stats_fbref (
    player_name     VARCHAR(255),
    team_name       VARCHAR(255),
    minutes_played  INT,
    goals           INT,
    assists         INT,
    xg              DECIMAL(6,2),
    xa              DECIMAL(6,2),
    yellow_cards    INT,
    red_cards       INT,
    shots           INT,
    shots_on_target INT,
    season_label    VARCHAR(9),
    load_timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stg_referee_raw (
    referee_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255),
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20),
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Raw referee data fields
    referee_name VARCHAR(255),
    date_of_birth DATE,
    nationality VARCHAR(100),
    premier_league_debut DATE,
    ref_status VARCHAR(50),
    notes TEXT,
    -- Indexes for performance and audit trail
    INDEX idx_file_name (file_name),
    INDEX idx_status (status),
    INDEX idx_load_start_time (load_start_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- StatsBomb Events Staging Table
CREATE TABLE IF NOT EXISTS stg_events_raw (
    event_id VARCHAR(50) NOT NULL PRIMARY KEY,
    statsbomb_match_id INT NOT NULL,
    statsbomb_period INT,
    timestamp VARCHAR(30),
    minute INT,
    second INT,
    type VARCHAR(100),
    player_name VARCHAR(255),
    player_id INT,
    team_name VARCHAR(255),
    team_id INT,
    position VARCHAR(100),
    possession_team_name VARCHAR(255),
    play_pattern VARCHAR(100),
    tactics_formation VARCHAR(50),
    carry_end_location JSON,
    pass_recipient_name VARCHAR(255),
    pass_length DECIMAL(10,2),
    shot_outcome VARCHAR(50),
    shot_xg DECIMAL(10,6),
    duel_outcome VARCHAR(50),
    raw_data JSON,
    status VARCHAR(20) DEFAULT 'LOADED',
    load_start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_statsbomb_match_id (statsbomb_match_id),
    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_player_name (player_name),
    INDEX idx_team_name (team_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- JSON STAGING TABLES
CREATE TABLE IF NOT EXISTS stg_player_raw (
    json_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    season INT,
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20),
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Raw player data fields
    player_id INT,
    player_name VARCHAR(255),
    team VARCHAR(255),
    position VARCHAR(50),
    raw_data JSON,
    -- Indexes for performance and audit trail
    INDEX idx_file_name (file_name),
    INDEX idx_file_path (file_path),
    INDEX idx_season (season),
    INDEX idx_player_id (player_id),
    INDEX idx_team (team),
    INDEX idx_status (status),
    INDEX idx_load_start_time (load_start_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ETL_JSON_Manifest (
    manifest_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    season INT,
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL,
    rows_processed INT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_name (file_name),
    INDEX idx_season (season),
    INDEX idx_status (status),
    INDEX idx_load_start_time (load_start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- DIMENSIONS
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT NOT NULL PRIMARY KEY,
    cal_date DATE NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    week INT NOT NULL,
    is_matchday TINYINT(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS dim_team (
    team_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    team_code VARCHAR(50),
    team_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    eff_start DATE NOT NULL DEFAULT '1900-01-01',
    eff_end DATE NOT NULL DEFAULT '9999-12-31',
    is_current CHAR(1) NOT NULL DEFAULT 'Y',
    UNIQUE KEY uk_team_name (team_name),
    UNIQUE KEY uk_team_code (team_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS dim_player (
    player_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    external_id VARCHAR(100),
    player_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    nationality VARCHAR(100),
    position VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    player_bk VARCHAR(80) UNIQUE,
    INDEX idx_player_name (player_name),
    UNIQUE KEY uk_external_id (external_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS dim_stadium (
    stadium_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    stadium_name VARCHAR(255),
    capacity INT,
    city VARCHAR(100),
    club VARCHAR(255),
    opened INT,
    coordinates VARCHAR(100),
    notes TEXT,
    stadium_bk VARCHAR(80) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS dim_referee (
    referee_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    referee_name VARCHAR(255),
    referee_name_short VARCHAR(100),
    date_of_birth DATE,
    nationality VARCHAR(100),
    premier_league_debut DATE,
    status VARCHAR(50),
    referee_bk VARCHAR(80) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS dim_season (
    season_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    season_name VARCHAR(20) NOT NULL,
    start_date DATE,
    end_date DATE,
    UNIQUE KEY uk_season_name (season_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- FACTS
CREATE TABLE IF NOT EXISTS fact_match (
    match_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    match_source_key VARCHAR(255) UNIQUE,
    date_id INT NOT NULL,
    season_id INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    referee_id INT NOT NULL DEFAULT -1,
    stadium_id INT NOT NULL DEFAULT -1,

    home_goals INT DEFAULT 0,
    away_goals INT DEFAULT 0,
    match_result CHAR(1),
    half_time_home_goals INT,
    half_time_away_goals INT,
    home_shots_total INT,
    away_shots_total INT,
    home_shots_on_target INT,
    away_shots_on_target INT,
    home_fouls INT,
    away_fouls INT,
    home_corners INT,
    away_corners INT,
    home_yellow_cards INT,
    away_yellow_cards INT,
    home_red_cards INT,
    away_red_cards INT,

    attendance INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (season_id) REFERENCES dim_season(season_id),
    FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (stadium_id) REFERENCES dim_stadium(stadium_id),
    FOREIGN KEY (referee_id) REFERENCES dim_referee(referee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX idx_date_year_month ON dim_date (year, month);
CREATE INDEX idx_team_code ON dim_team (team_code);

CREATE TABLE IF NOT EXISTS fact_match_events (
    event_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    event_type VARCHAR(50),
    player_id INT,
    team_id INT,
    minute INT,
    extra_time INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES fact_match(match_id),
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id),
    INDEX (match_id),
    INDEX (player_id),
    INDEX (team_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS fact_player_stats (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    player_id INT NOT NULL,
    team_id INT,
    minutes_played INT,
    goals INT DEFAULT 0,
    assists INT DEFAULT 0,
    yellow_cards INT DEFAULT 0,
    red_cards INT DEFAULT 0,
    shots INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES fact_match(match_id),
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id),
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id),
    INDEX (match_id),
    INDEX (player_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Sentinel rows (unknown) for FK safety
INSERT IGNORE dim_date      (date_id,cal_date,year,month,day,week) VALUES (-1,'1900-01-01',1900,1,1,1);
INSERT IGNORE dim_team      (team_id,team_name) VALUES (-1,'Unknown Team');
INSERT IGNORE dim_referee   (referee_id,referee_name) VALUES (-1,'Unknown Referee');
INSERT IGNORE dim_stadium   (stadium_id,stadium_name) VALUES (-1,'Unknown Stadium');
INSERT IGNORE dim_season    (season_id,season_name) VALUES (-1,'Unknown Season');

-- Load calendar (1992-2040) - idempotent
INSERT IGNORE dim_date (date_id,cal_date,year,month,day,week)
SELECT DATE_FORMAT(d,'%Y%m%d'), d, YEAR(d), MONTH(d), DAY(d), WEEKOFYEAR(d)
FROM (
      SELECT DATE('1992-07-01') + INTERVAL (a.a + (10 * b.a) + (100 * c.a) + (1000 * d.a) + (10000 * e.a)) DAY AS d
      FROM (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
      CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
      CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) c
      CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) d
      CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) e
) t
WHERE d BETWEEN '1992-07-01' AND '2040-06-30';

-- Initial seasons
INSERT IGNORE dim_season (season_name,start_date,end_date) VALUES
('2020/2021','2020-09-12','2021-05-23'),
('2021/2022','2021-08-13','2022-05-22'),
('2022/2023','2022-08-05','2023-05-28'),
('2023/2024','2023-08-11','2024-05-19'),
('2024/2025','2024-08-16','2025-05-25'),
('2025/2026','2025-08-15','2026-05-24');
-- Add check constraints if they do not already exist (MySQL doesn't support IF NOT EXISTS for constraints)
-- We'll create them only when not present.
SET @c1 := (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='fact_match' AND CONSTRAINT_NAME='chk_hg');
SET @c2 := (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='fact_match' AND CONSTRAINT_NAME='chk_ag');
-- Add chk_hg
SET @s = NULL;
SELECT IF(@c1=0, 'ALTER TABLE fact_match ADD CONSTRAINT chk_hg CHECK (home_goals BETWEEN 0 AND 20);', 'SELECT "chk_hg exists";') INTO @s;
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
-- Add chk_ag
SELECT IF(@c2=0, 'ALTER TABLE fact_match ADD CONSTRAINT chk_ag CHECK (away_goals BETWEEN 0 AND 20);', 'SELECT "chk_ag exists";') INTO @s;
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;
-- End of canonical schema
