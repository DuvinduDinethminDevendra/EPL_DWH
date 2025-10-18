-- D:\myPortfolioProject\EPL_DWH\src\sql\create_schema.sql

CREATE DATABASE IF NOT EXISTS epl_dw;
USE epl_dw;

-- Disable foreign key checks temporarily to allow dropping tables in any order
SET FOREIGN_KEY_CHECKS = 0;

-- Drop Fact tables first
DROP TABLE IF EXISTS fact_player_stats;
DROP TABLE IF EXISTS fact_match_events;
DROP TABLE IF EXISTS fact_match;

-- Drop Dimension tables
DROP TABLE IF EXISTS dim_referee;
DROP TABLE IF EXISTS dim_stadium;
DROP TABLE IF EXISTS dim_player;
DROP TABLE IF EXISTS dim_team;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_season;

-- Drop Staging and Control tables
DROP TABLE IF EXISTS ETL_Log;
DROP TABLE IF EXISTS ETL_File_Manifest;

-- Drop old, generic staging tables (if they exist)
DROP TABLE IF EXISTS staging_matches;
DROP TABLE IF EXISTS staging_players;
DROP TABLE IF EXISTS staging_teams;
DROP TABLE IF EXISTS staging_referees;
DROP TABLE IF EXISTS staging_dates;
DROP TABLE IF EXISTS stg_e0_match_raw;  


-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;


-- CONTROL TABLE


CREATE TABLE IF NOT EXISTS ETL_Log (
    log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    phase_step VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    rows_processed INT,
    message TEXT
) ENGINE=InnoDB;

-- table to track the status of raw source files
CREATE TABLE IF NOT EXISTS ETL_File_Manifest (
    file_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE, -- The Natural Key for the file
    league_div VARCHAR(5) NOT NULL,         -- e.g., 'E0'
    load_start_time DATETIME NOT NULL,
    load_end_time DATETIME,
    status VARCHAR(20) NOT NULL,            -- 'SUCCESS', 'FAILED', 'IN_PROGRESS'
    rows_processed INT,
    error_message TEXT
) ENGINE=InnoDB;



-- STAGING TABLES (By Entity)


-- CRITICAL: Raw Staging Table for the entire E0 CSV data (NON-BETTING COLUMNS ONLY)
-- This captures all data necessary for Dims and Facts.
CREATE TABLE IF NOT EXISTS stg_e0_match_raw (
    match_source_key VARCHAR(255) NOT NULL PRIMARY KEY, 
    `Div` VARCHAR(5),
    `Date` DATE,
    `Time` TIME,
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
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS staging_players (
    player_id VARCHAR(100),
    player_name VARCHAR(255),
    birth_date DATE,
    nationality VARCHAR(100),
    position VARCHAR(50)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS staging_teams (
    team_code VARCHAR(50),
    team_name VARCHAR(255),
    city VARCHAR(100)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS staging_referees (
    referee_name VARCHAR(255),
    country VARCHAR(100)
) ENGINE=InnoDB;



-- DIMENSION TABLES 


CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT NOT NULL PRIMARY KEY,
    cal_date DATE NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    week INT NOT NULL,
    is_matchday TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_team (
    team_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    team_code VARCHAR(50),
    team_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (team_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_player (
    player_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    external_id VARCHAR(100),
    player_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    nationality VARCHAR(100),
    position VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (external_id),
    INDEX (player_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_stadium (
    stadium_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    stadium_name VARCHAR(255),
    capacity INT,
    city VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_referee (
    referee_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    referee_name VARCHAR(255),
    country VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_season (
    season_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    season_name VARCHAR(20) NOT NULL,
    start_date DATE,
    end_date DATE,
    UNIQUE KEY (season_name)
) ENGINE=InnoDB;


-- FACT TABLES

-- Fact_Match (Redesigned structure)
CREATE TABLE IF NOT EXISTS fact_match (
    match_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    date_id INT NOT NULL,
    season_id INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    referee_id INT,
    stadium_id INT,
    
    -- CORE RESULTS & STATS (Metrics derived from E0 CSV)
    home_goals INT DEFAULT 0,
    away_goals INT DEFAULT 0,
    match_result CHAR(1),                  -- FTR
    half_time_home_goals INT,              -- HTHG
    half_time_away_goals INT,              -- HTAG
    home_shots_total INT,                  -- HS
    away_shots_total INT,                  -- AS
    home_shots_on_target INT,              -- HST
    away_shots_on_target INT,              -- AST
    home_fouls INT,                        -- HF
    away_fouls INT,                        -- AF
    home_corners INT,                      -- HC
    away_corners INT,                      -- AC
    home_yellow_cards INT,                 -- HY
    away_yellow_cards INT,                 -- AY
    home_red_cards INT,                    -- HR
    away_red_cards INT,                    -- AR
    
    attendance INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (season_id) REFERENCES dim_season(season_id),
    FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id),
    FOREIGN KEY (stadium_id) REFERENCES dim_stadium(stadium_id),
    FOREIGN KEY (referee_id) REFERENCES dim_referee(referee_id)
) ENGINE=InnoDB;

-- Fact_Match_Events (Kept original structure)
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
) ENGINE=InnoDB;

-- Fact_Player_Stats (Kept original structure)
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
) ENGINE=InnoDB;

-- End of create_schema.sql