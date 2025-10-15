-- D:\myPortfolioProject\EPL_DWH\src\sql\create_schema.sql

CREATE DATABASE IF NOT EXISTS epl_dw;
USE epl_dw;

-- Disable foreign key checks temporarily to allow dropping tables in any order
SET FOREIGN_KEY_CHECKS = 0;

-- Drop Fact tables first (to avoid foreign key constraints blocking drops)
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

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;


-- Dim_Date
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_date (
	date_id INT NOT NULL PRIMARY KEY,
	cal_date DATE NOT NULL,
	year INT NOT NULL,
	month INT NOT NULL,
	day INT NOT NULL,
	week INT NOT NULL,
	is_matchday TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;

-- Dim_Team
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_team (
	team_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	team_code VARCHAR(50),
	team_name VARCHAR(255) NOT NULL,
	city VARCHAR(100),
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE KEY (team_name)
) ENGINE=InnoDB;

-- Dim_Player (simple SCD1)
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_player (
	player_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	external_id VARCHAR(100), -- e.g., fbref id
	player_name VARCHAR(255) NOT NULL,
	birth_date DATE,
	nationality VARCHAR(100),
	position VARCHAR(50),
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE KEY (external_id),
	INDEX (player_name)
) ENGINE=InnoDB;

-- Dim_Stadium
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_stadium (
	stadium_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	stadium_name VARCHAR(255),
	capacity INT,
	city VARCHAR(100)
) ENGINE=InnoDB;

-- Dim_Referee
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_referee (
	referee_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	referee_name VARCHAR(255),
	country VARCHAR(100)
) ENGINE=InnoDB;

-- Dim_Season
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS dim_season (
	season_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	season_name VARCHAR(20) NOT NULL,  -- e.g., '2024-25'
	start_date DATE,
	end_date DATE,
	UNIQUE KEY (season_name)
) ENGINE=InnoDB;

-- Fact_Match (one row per match)
-- FIX: Changed match_id from BIGINT to INT to resolve the foreign key incompatibility (Error 3780)
CREATE TABLE IF NOT EXISTS fact_match (
	match_id INT NOT NULL PRIMARY KEY, -- Changed from BIGINT
	date_id INT NOT NULL,
	season VARCHAR(20),
	home_team_id INT NOT NULL,
	away_team_id INT NOT NULL,
	home_goals INT DEFAULT 0,
	away_goals INT DEFAULT 0,
	attendance INT,
	stadium_id INT,
	referee_id INT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
	FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id),
	FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id),
	FOREIGN KEY (stadium_id) REFERENCES dim_stadium(stadium_id),
	FOREIGN KEY (referee_id) REFERENCES dim_referee(referee_id)
) ENGINE=InnoDB;

-- Fact_Match_Events
-- FIX: Changed match_id from BIGINT to INT to resolve the foreign key incompatibility (Error 3780)
CREATE TABLE IF NOT EXISTS fact_match_events (
	event_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, -- Kept BIGINT for max events
	match_id INT NOT NULL, -- Changed from BIGINT
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

-- Fact_Player_Stats (one row per player per match)
-- Note: Reusing the structure from the original create_schema.sql
CREATE TABLE IF NOT EXISTS fact_player_stats (
	id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, -- Kept BIGINT for max stats rows
	match_id INT NOT NULL, -- Changed from BIGINT to match Fact_Match
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


-- Add the season_id foreign key constraint, which was an ALTER statement in the original script
ALTER TABLE fact_match ADD COLUMN season_id INT;
ALTER TABLE fact_match ADD FOREIGN KEY (season_id) REFERENCES dim_season(season_id);