# EPL Data Warehouse - Complete Database Schema Structure

Complete reference guide for all 21 tables in the EPL DWH database with column definitions, data types, constraints, and relationships.

---

## 📊 Database Overview

**Database Name:** `epl_dw`  
**Character Set:** UTF8MB4  
**Collation:** utf8mb4_0900_ai_ci  
**Total Tables:** 21  
**Engine:** InnoDB (with FK constraints)

---

## Table Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                     21 TABLES ORGANIZED AS                      │
├─────────────────────────────────────────────────────────────────┤
│ DIMENSIONS (6)        │ FACTS (3)          │ MAPPINGS (2)       │
├───────────────────────┼────────────────────┼────────────────────┤
│ dim_date              │ fact_match         │ dim_team_mapping   │
│ dim_team              │ fact_match_events  │ dim_match_mapping  │
│ dim_player            │ fact_player_stats  │                    │
│ dim_referee           │                    │ STAGING (7)        │
│ dim_stadium           │                    ├────────────────────┤
│ dim_season            │                    │ stg_e0_match_raw   │
│                       │                    │ stg_team_raw       │
│ ETL METADATA (3)      │                    │ stg_player_raw     │
├───────────────────────┤                    │ stg_events_raw     │
│ etl_log               │                    │ stg_player_stats..│
│ etl_file_manifest     │                    │ stg_referee_raw    │
│ etl_api_manifest      │                    │ (+ 3 more)         │
└───────────────────────┴────────────────────┴────────────────────┘
```

---

# 📋 DIMENSION TABLES

## 1. dim_date (Calendar Dimension)

**Purpose:** Conformed date dimension for all date-based queries  
**Rows:** 17,533 (1992-07-01 to 2040-06-30)  
**Primary Key:** date_id (YYYYMMDD format)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `date_id` | INT | PK | Date in YYYYMMDD format (e.g., 20230114) |
| `cal_date` | DATE | NOT NULL | Actual calendar date (e.g., 2023-01-14) |
| `year` | INT | NOT NULL | Year (e.g., 2023) |
| `month` | INT | NOT NULL | Month (1-12) |
| `day` | INT | NOT NULL | Day of month (1-31) |
| `week` | INT | NOT NULL | Week of year (1-53) |
| `is_matchday` | TINYINT(1) | DEFAULT 0 | Flag for EPL match days (0/1) |

**Indexes:**
- `PRIMARY KEY (date_id)`
- `idx_date_year_month (year, month)` — Quick filtering by year/month

**Sentinel Row:** `date_id=-1, cal_date=1900-01-01` (for unknown dates)

**Sample Data:**
```
date_id  | cal_date   | year | month | day | week | is_matchday
─────────────────────────────────────────────────────────────────
-1       | 1900-01-01 | 1900 | 1     | 1   | 1    | 0
19920701 | 1992-07-01 | 1992 | 7     | 1   | 27   | 0
20230114 | 2023-01-14 | 2023 | 1     | 14  | 2    | 1
```

---

## 2. dim_team (Team Master Data)

**Purpose:** Conformed team dimension  
**Rows:** 31 (23 EPL teams + 1 UNKNOWN sentinel)  
**Primary Key:** team_id (Surrogate key)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `team_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `team_code` | VARCHAR(50) | UNIQUE | 3-letter team code (e.g., ARS, CHE) |
| `team_name` | VARCHAR(255) | NOT NULL, UNIQUE | Full team name (e.g., Arsenal) |
| `city` | VARCHAR(100) | - | City where team is based |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |
| `eff_start` | DATE | NOT NULL | Effective start date (SCD Type 2) |
| `eff_end` | DATE | NOT NULL | Effective end date (SCD Type 2) |
| `is_current` | CHAR(1) | NOT NULL DEFAULT 'Y' | Current version flag (Y/N) |

**Indexes:**
- `PRIMARY KEY (team_id)`
- `UNIQUE KEY uk_team_name (team_name)`
- `UNIQUE KEY uk_team_code (team_code)`
- `idx_team_code (team_code)` — Quick lookup by code

**Foreign Key Relationships:**
- Referenced by: `fact_match.home_team_id`, `fact_match.away_team_id`, `fact_match_events.team_id`, `fact_player_stats.team_id`, `dim_team_mapping.dim_team_id`

**Sentinel Row:** `team_id=-1, team_name='Unknown Team'`

**Sample Data:**
```
team_id | team_code | team_name      | city        | is_current
────────────────────────────────────────────────────────────────
-1      | UNK       | Unknown Team   | Unknown     | Y
1       | ARS       | Arsenal        | London      | Y
2       | AVL       | Aston Villa    | Birmingham  | Y
3       | CHE       | Chelsea        | London      | Y
...
```

---

## 3. dim_player (Player Master Data)

**Purpose:** Conformed player dimension  
**Rows:** 6,809 (including 1 UNKNOWN sentinel)  
**Primary Key:** player_id (Surrogate key)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `player_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `external_id` | VARCHAR(100) | UNIQUE | External system ID (StatsBomb, etc.) |
| `player_name` | VARCHAR(255) | NOT NULL | Player full name |
| `birth_date` | DATE | - | Date of birth |
| `nationality` | VARCHAR(100) | - | Player nationality |
| `position` | VARCHAR(50) | - | Playing position (GK, DEF, MID, FWD, etc.) |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |
| `player_bk` | VARCHAR(80) | UNIQUE | Business key (combination of name + DOB) |

**Indexes:**
- `PRIMARY KEY (player_id)`
- `UNIQUE KEY uk_external_id (external_id)`
- `UNIQUE KEY uk_player_bk (player_bk)`
- `idx_player_name (player_name)` — Quick lookup by name

**Foreign Key Relationships:**
- Referenced by: `fact_match_events.player_id`, `fact_player_stats.player_id`

**Sentinel Row:** `player_id=6808, player_name='UNKNOWN'`

**Sample Data:**
```
player_id | external_id | player_name      | birth_date | nationality | position
──────────────────────────────────────────────────────────────────────────────
6808      | NULL        | UNKNOWN          | NULL       | UNKNOWN     | UNKNOWN
1         | SB_12345    | Bukayo Saka      | 2001-09-05 | England     | MID
2         | SB_12346    | Martin Odegaard  | 1998-12-17 | Norway      | MID
...
```

---

## 4. dim_stadium (Stadium Master Data)

**Purpose:** Conformed stadium/venue dimension  
**Rows:** 58 (EPL stadiums + 1 UNKNOWN sentinel)  
**Primary Key:** stadium_id (Surrogate key)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `stadium_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `stadium_name` | VARCHAR(255) | - | Official stadium name |
| `capacity` | INT | - | Stadium seating capacity |
| `city` | VARCHAR(100) | - | City where stadium is located |
| `club` | VARCHAR(255) | - | Primary club that uses the stadium |
| `opened` | INT | - | Year stadium opened |
| `coordinates` | VARCHAR(100) | - | GPS coordinates (latitude, longitude) |
| `notes` | TEXT | - | Additional notes |
| `stadium_bk` | VARCHAR(80) | UNIQUE | Business key (stadium name) |

**Indexes:**
- `PRIMARY KEY (stadium_id)`
- `UNIQUE KEY uk_stadium_bk (stadium_bk)`

**Foreign Key Relationships:**
- Referenced by: `fact_match.stadium_id`

**Sentinel Row:** `stadium_id=-1, stadium_name='Unknown Stadium'`

**Sample Data:**
```
stadium_id | stadium_name       | capacity | city    | club        | opened | stadium_bk
───────────────────────────────────────────────────────────────────────────────────────
-1         | Unknown Stadium    | NULL     | Unknown | Unknown     | NULL   | UNKNOWN
1          | Emirates Stadium   | 60260    | London  | Arsenal     | 2006   | EMIRATES
2          | Villa Park         | 42682    | Birm... | Aston Villa | 1897   | VILLA_PARK
...
```

---

## 5. dim_referee (Referee Master Data)

**Purpose:** Conformed referee dimension  
**Rows:** 33 (EPL referees + 1 UNKNOWN sentinel)  
**Primary Key:** referee_id (Surrogate key)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `referee_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `referee_name` | VARCHAR(255) | - | Full name of referee |
| `referee_name_short` | VARCHAR(100) | - | Shortened/nick name |
| `date_of_birth` | DATE | - | Referee birth date |
| `nationality` | VARCHAR(100) | - | Nationality |
| `premier_league_debut` | DATE | - | First EPL match date |
| `status` | VARCHAR(50) | - | Current status (ACTIVE, RETIRED, etc.) |
| `referee_bk` | VARCHAR(80) | UNIQUE | Business key (referee name) |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (referee_id)`
- `UNIQUE KEY uk_referee_bk (referee_bk)`

**Foreign Key Relationships:**
- Referenced by: `fact_match.referee_id`

**Sentinel Row:** `referee_id=-1, referee_name='Unknown Referee'`

**Sample Data:**
```
referee_id | referee_name    | referee_name_short | nationality | premier_league_debut | status
──────────────────────────────────────────────────────────────────────────────────────────────
-1         | Unknown Referee | UNK                | Unknown     | NULL                 | ACTIVE
1          | Mike Dean       | MD                 | England     | 1992-05-23           | RETIRED
2          | Anthony Taylor  | AT                 | England     | 2009-08-29           | ACTIVE
...
```

---

## 6. dim_season (Season Master Data)

**Purpose:** Conformed season dimension  
**Rows:** 9 (2017/18 through 2025/26 + 1 UNKNOWN sentinel)  
**Primary Key:** season_id (Surrogate key)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `season_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `season_name` | VARCHAR(20) | NOT NULL, UNIQUE | Season label (e.g., '2023/2024') |
| `start_date` | DATE | - | First day of season |
| `end_date` | DATE | - | Last day of season |

**Indexes:**
- `PRIMARY KEY (season_id)`
- `UNIQUE KEY uk_season_name (season_name)`

**Foreign Key Relationships:**
- Referenced by: `fact_match.season_id`

**Sentinel Row:** `season_id=-1, season_name='Unknown Season'`

**Sample Data:**
```
season_id | season_name | start_date | end_date
───────────────────────────────────────────────
-1        | Unknown...  | NULL       | NULL
1         | 2017/2018   | 2017-08-11 | 2018-05-13
2         | 2018/2019   | 2018-08-10 | 2019-05-12
3         | 2019/2020   | 2019-08-09 | 2020-07-26
...
9         | 2024/2025   | 2024-08-16 | 2025-05-25
```

---

# 📊 FACT TABLES

## 1. fact_match (Match-Level Facts)

**Purpose:** Central fact table for EPL matches  
**Rows:** 830 (2017/18 - 2024/25 seasons)  
**Primary Key:** match_id (Surrogate key)  
**Granularity:** One row per match

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `match_id` | INT | PK, AUTO_INCREMENT | Surrogate key |
| `match_source_key` | VARCHAR(255) | UNIQUE | Business key from source (date + teams) |
| `date_id` | INT | NOT NULL, FK | Links to dim_date |
| `season_id` | INT | NOT NULL, FK | Links to dim_season |
| `home_team_id` | INT | NOT NULL, FK | Links to dim_team (home) |
| `away_team_id` | INT | NOT NULL, FK | Links to dim_team (away) |
| `referee_id` | INT | FK, DEFAULT -1 | Links to dim_referee |
| `stadium_id` | INT | FK, DEFAULT -1 | Links to dim_stadium |
| `home_goals` | INT | DEFAULT 0 | Goals scored by home team |
| `away_goals` | INT | DEFAULT 0 | Goals scored by away team |
| `match_result` | CHAR(1) | - | Result (H=Home win, D=Draw, A=Away win) |
| `half_time_home_goals` | INT | - | HT goals by home team |
| `half_time_away_goals` | INT | - | HT goals by away team |
| `home_shots_total` | INT | - | Total shots by home team |
| `away_shots_total` | INT | - | Total shots by away team |
| `home_shots_on_target` | INT | - | On-target shots by home team |
| `away_shots_on_target` | INT | - | On-target shots by away team |
| `home_fouls` | INT | - | Fouls committed by home team |
| `away_fouls` | INT | - | Fouls committed by away team |
| `home_corners` | INT | - | Corners won by home team |
| `away_corners` | INT | - | Corners won by away team |
| `home_yellow_cards` | INT | - | Yellow cards given to home team |
| `away_yellow_cards` | INT | - | Yellow cards given to away team |
| `home_red_cards` | INT | - | Red cards given to home team |
| `away_red_cards` | INT | - | Red cards given to away team |
| `attendance` | INT | - | Match attendance |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (match_id)`
- `UNIQUE KEY uk_match_source_key (match_source_key)`

**Foreign Keys:**
```sql
FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
FOREIGN KEY (season_id) REFERENCES dim_season(season_id),
FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id),
FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id),
FOREIGN KEY (stadium_id) REFERENCES dim_stadium(stadium_id),
FOREIGN KEY (referee_id) REFERENCES dim_referee(referee_id)
```

**Check Constraints:**
- `chk_hg: home_goals BETWEEN 0 AND 20`
- `chk_ag: away_goals BETWEEN 0 AND 20`

**Sample Row:**
```
match_id | date_id  | season_id | home_team_id | away_team_id | home_goals | away_goals | attendance
─────────────────────────────────────────────────────────────────────────────────────────────────
1        | 20230114 | 3         | 1 (ARS)      | 2 (AVL)      | 2          | 0          | 60389
```

---

## 2. fact_match_events (Match Event Facts)

**Purpose:** Event-level facts from StatsBomb data  
**Rows:** 1,362,577 (all events: passes, shots, fouls, etc.)  
**Primary Key:** event_id (Surrogate key)  
**Granularity:** One row per match event

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `event_id` | BIGINT | PK, AUTO_INCREMENT | Surrogate key |
| `match_id` | INT | NOT NULL, FK | Links to fact_match |
| `event_type` | VARCHAR(50) | - | Type of event (Pass, Shot, Foul, etc.) |
| `player_id` | INT | FK | Links to dim_player (who performed event) |
| `team_id` | INT | FK | Links to dim_team (which team) |
| `minute` | INT | - | Minute of match (0-120+) |
| `extra_time` | INT | DEFAULT 0 | Extra time in seconds |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (event_id)`
- `INDEX (match_id)` — Queries by match
- `INDEX (player_id)` — Queries by player
- `INDEX (team_id)` — Queries by team

**Foreign Keys:**
```sql
FOREIGN KEY (match_id) REFERENCES fact_match(match_id),
FOREIGN KEY (player_id) REFERENCES dim_player(player_id),
FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
```

**Event Types Found:**
- Pass, Shot, Foul Committed, Duel, Interception, Clearance, Aerial, Tackle, Carry, Dispossessed, Error, Shield Ball Out, Dribble, Substitution, Error, Own Goal

**Sample Rows:**
```
event_id | match_id | event_type      | player_id | team_id | minute
─────────────────────────────────────────────────────────────────────
1        | 1        | Pass            | 10        | 1 (ARS) | 1
2        | 1        | Pass            | 5         | 1 (ARS) | 1
3        | 1        | Shot            | 15        | 1 (ARS) | 12
4        | 1        | Foul Committed  | 8         | 2 (AVL) | 25
...
1362577  | 830      | Substitution    | NULL      | 2 (AVL) | 88
```

---

## 3. fact_player_stats (Player Statistics Per Match)

**Purpose:** Player performance stats aggregated per match  
**Rows:** 0 (currently - optional feature)  
**Primary Key:** id (Surrogate key)  
**Granularity:** One row per player per match

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGINT | PK, AUTO_INCREMENT | Surrogate key |
| `match_id` | INT | NOT NULL, FK | Links to fact_match |
| `player_id` | INT | NOT NULL, FK | Links to dim_player |
| `team_id` | INT | FK | Links to dim_team |
| `minutes_played` | INT | - | Minutes player was on field |
| `goals` | INT | DEFAULT 0 | Goals scored by player |
| `assists` | INT | DEFAULT 0 | Assists by player |
| `yellow_cards` | INT | DEFAULT 0 | Yellow cards received |
| `red_cards` | INT | DEFAULT 0 | Red cards received |
| `shots` | INT | DEFAULT 0 | Total shots taken |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX (match_id)`
- `INDEX (player_id)`

**Foreign Keys:**
```sql
FOREIGN KEY (match_id) REFERENCES fact_match(match_id),
FOREIGN KEY (player_id) REFERENCES dim_player(player_id),
FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
```

**Sample Row (if populated):**
```
id | match_id | player_id | team_id | minutes_played | goals | assists | shots
────────────────────────────────────────────────────────────────────────────────
1  | 1        | 10        | 1 (ARS) | 90             | 1     | 0       | 3
```

---

# 🔗 MAPPING TABLES

## 1. dim_team_mapping (Team ID Bridge)

**Purpose:** Maps StatsBomb team IDs to dim_team surrogate keys  
**Rows:** 40 (17 EPL teams + 7 international + sentinels)  
**Primary Key:** statsbomb_team_id  
**Type:** Bridge table for ETL integration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `statsbomb_team_id` | INT | PK | StatsBomb team ID |
| `dim_team_id` | INT | NOT NULL, FK | Links to dim_team |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (statsbomb_team_id)`
- `INDEX idx_dim_team (dim_team_id)` — Reverse lookup

**Foreign Keys:**
```sql
FOREIGN KEY (dim_team_id) REFERENCES dim_team(team_id)
```

**Sample Data:**
```
statsbomb_team_id | dim_team_id | Team Name
─────────────────────────────────────────
1                 | 1           | Arsenal
22                | 2           | Aston Villa
23                | 3           | Chelsea
...
30                | -1          | (International)
31                | -1          | (International)
```

---

## 2. dim_match_mapping (Match ID Bridge)

**Purpose:** Maps StatsBomb match IDs to CSV match IDs (fact_match)  
**Rows:** 684 (380 EPL + 304 other matches)  
**Primary Key:** statsbomb_match_id  
**Type:** Bridge table for data reconciliation

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `statsbomb_match_id` | INT | PK | StatsBomb match ID |
| `csv_match_id` | INT | NOT NULL, FK | Links to fact_match.match_id |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `PRIMARY KEY (statsbomb_match_id)`
- `INDEX idx_csv_match (csv_match_id)` — Reverse lookup

**Foreign Keys:**
```sql
FOREIGN KEY (csv_match_id) REFERENCES fact_match(match_id)
```

**Sample Data:**
```
statsbomb_match_id | csv_match_id | Home Team      | Away Team
──────────────────────────────────────────────────────────────
3242891            | 1            | Arsenal        | Bournemouth
3242892            | 2            | Chelsea        | Crystal Palace
...
3242892            | 380          | (International)| (International)
```

---

# 📁 STAGING TABLES

## 1. stg_e0_match_raw (CSV Match Staging)

**Purpose:** Intermediate staging for raw CSV match data  
**Rows:** 830 (all EPL matches)  
**Primary Key:** match_source_key (Business key)  
**Loaded from:** E0.csv (seasons 2017/18 through 2024/25)

| Column | Type | Description |
|--------|------|-------------|
| `match_source_key` | VARCHAR(255) | PK - Composite key (date + teams) |
| `Div` | VARCHAR(5) | League division (E0 = English Premier League) |
| `Date` | DATE | Match date |
| `Time` | TIME | Kick-off time |
| `season` | VARCHAR(20) | Season label (e.g., '2023/2024') |
| `HomeTeam` | VARCHAR(255) | Home team name |
| `AwayTeam` | VARCHAR(255) | Away team name |
| `FTHG` | INT | Full-time home goals |
| `FTAG` | INT | Full-time away goals |
| `FTR` | CHAR(1) | Full-time result (H/D/A) |
| `HTHG` | INT | Half-time home goals |
| `HTAG` | INT | Half-time away goals |
| `HTR` | CHAR(1) | Half-time result (H/D/A) |
| `Referee` | VARCHAR(255) | Referee name |
| `HS` | INT | Home shots |
| `AS` | INT | Away shots |
| `HST` | INT | Home shots on target |
| `AST` | INT | Away shots on target |
| `HF` | INT | Home fouls |
| `AF` | INT | Away fouls |
| `HC` | INT | Home corners |
| `AC` | INT | Away corners |
| `HY` | INT | Home yellow cards |
| `AY` | INT | Away yellow cards |
| `HR` | INT | Home red cards |
| `AR` | INT | Away red cards |
| `load_timestamp` | DATETIME | When this row was loaded |

**Indexes:**
- `PRIMARY KEY (match_source_key)`

---

## 2. stg_events_raw (StatsBomb Events Staging)

**Purpose:** Intermediate staging for raw StatsBomb event data  
**Rows:** 1,362,577 (all events from JSON files)  
**Primary Key:** event_id (Business key)  
**Loaded from:** StatsBomb match.json files

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | VARCHAR(50) | PK - UUID from StatsBomb |
| `statsbomb_match_id` | INT | Match ID from StatsBomb |
| `statsbomb_period` | INT | Period number (1st half, 2nd half, etc.) |
| `timestamp` | VARCHAR(30) | Event timestamp (ISO format) |
| `minute` | INT | Minute of match |
| `second` | INT | Second within minute |
| `type` | VARCHAR(100) | Event type (Pass, Shot, Foul, etc.) |
| `player_name` | VARCHAR(255) | Player name |
| `player_id` | INT | StatsBomb player ID |
| `team_name` | VARCHAR(255) | Team name |
| `team_id` | INT | StatsBomb team ID |
| `position` | VARCHAR(100) | Player position at time of event |
| `possession_team_name` | VARCHAR(255) | Team with possession |
| `play_pattern` | VARCHAR(100) | Pattern of play (e.g., "open play") |
| `tactics_formation` | VARCHAR(50) | Formation used (e.g., "4-3-3") |
| `carry_end_location` | JSON | Coordinates of end location (for carries) |
| `pass_recipient_name` | VARCHAR(255) | Recipient of pass (if applicable) |
| `pass_length` | DECIMAL(10,2) | Length of pass in meters |
| `shot_outcome` | VARCHAR(50) | Outcome (Goal, Saved, Blocked, etc.) |
| `shot_xg` | DECIMAL(10,6) | Expected goals value for shot |
| `duel_outcome` | VARCHAR(50) | Outcome of duel |
| `raw_data` | JSON | Full raw event JSON object |
| `status` | VARCHAR(20) | Processing status (LOADED, ERROR, etc.) |
| `load_start_time` | DATETIME | When load began |
| `created_at` | DATETIME | When row was created |

**Indexes:**
- `PRIMARY KEY (event_id)`
- `INDEX idx_statsbomb_match_id (statsbomb_match_id)` — Query by match
- `INDEX idx_type (type)` — Query by event type
- `INDEX idx_status (status)` — Monitor processing
- `INDEX idx_player_name (player_name)` — Query by player
- `INDEX idx_team_name (team_name)` — Query by team

---

## 3. stg_team_raw (Team API Staging)

**Purpose:** Intermediate staging for raw team data from external APIs  
**Rows:** ~600  
**Loaded from:** FootballData.org API

| Column | Type | Description |
|--------|------|-------------|
| `api_id` | INT | PK - Auto-increment |
| `api_name` | VARCHAR(255) | API source name (e.g., 'FootballData.org') |
| `endpoint` | VARCHAR(255) | API endpoint called |
| `team_id` | INT | External team ID |
| `load_start_time` | DATETIME | When load began |
| `load_end_time` | DATETIME | When load completed |
| `status` | VARCHAR(20) | Load status |
| `rows_processed` | INT | Count of rows processed |
| `error_message` | TEXT | Error details if failed |
| `created_at` | DATETIME | Row creation timestamp |
| `name` | VARCHAR(255) | Team name |
| `shortName` | VARCHAR(255) | Short team name |
| `tla` | VARCHAR(10) | Three-letter abbreviation |
| `crest` | VARCHAR(512) | Team crest URL |
| `address` | VARCHAR(255) | Team address |
| `website` | VARCHAR(255) | Team website |
| `founded` | INT | Year team was founded |
| `clubColors` | VARCHAR(100) | Club colors |
| `venue` | VARCHAR(255) | Stadium name |
| `runningCompetitions` | JSON | Current competitions JSON |
| `squad` | JSON | Squad players JSON |
| `staff` | JSON | Staff JSON |
| `lastUpdated` | DATETIME | Last update timestamp |
| `area_id` | INT | Geographic area ID |
| `area_name` | VARCHAR(255) | Geographic area name |
| `area_code` | VARCHAR(10) | Area country code |
| `area_flag` | VARCHAR(512) | Flag emoji/image |
| `coach_id` | INT | Head coach ID |
| `coach_firstName` | VARCHAR(100) | Coach first name |
| `coach_lastName` | VARCHAR(100) | Coach last name |
| `coach_name` | VARCHAR(255) | Coach full name |
| `coach_dateOfBirth` | DATE | Coach birth date |
| `coach_nationality` | VARCHAR(100) | Coach nationality |
| `coach_contract_start` | DATE | Coach contract start |
| `coach_contract_until` | DATE | Coach contract end |

**Indexes:**
- `PRIMARY KEY (api_id)`
- `INDEX idx_api_name (api_name)`
- `INDEX idx_endpoint (endpoint)`
- `INDEX idx_team_id (team_id)`
- `INDEX idx_status (status)`
- `INDEX idx_load_start_time (load_start_time)`

---

## 4. stg_player_raw (Player JSON Staging)

**Purpose:** Intermediate staging for raw player data from JSON files  
**Rows:** ~7,000  
**Loaded from:** StatsBomb player.json files

| Column | Type | Description |
|--------|------|-------------|
| `json_id` | INT | PK - Auto-increment |
| `file_name` | VARCHAR(255) | Source JSON file name |
| `file_path` | VARCHAR(255) | Full file path |
| `season` | INT | Season (year) |
| `load_start_time` | DATETIME | Load start timestamp |
| `load_end_time` | DATETIME | Load end timestamp |
| `status` | VARCHAR(20) | Load status |
| `rows_processed` | INT | Count of rows processed |
| `error_message` | TEXT | Error details if failed |
| `created_at` | DATETIME | Row creation timestamp |
| `player_id` | INT | External player ID |
| `player_name` | VARCHAR(255) | Player name |
| `team` | VARCHAR(255) | Team name |
| `position` | VARCHAR(50) | Player position |
| `raw_data` | JSON | Full raw player JSON object |

**Indexes:**
- `PRIMARY KEY (json_id)`
- `INDEX idx_file_name (file_name)`
- `INDEX idx_file_path (file_path)`
- `INDEX idx_season (season)`
- `INDEX idx_player_id (player_id)`
- `INDEX idx_team (team)`
- `INDEX idx_status (status)`

---

## 5. stg_player_stats_fbref (Player Stats FBRef Staging)

**Purpose:** Intermediate staging for player stats from FBRef  
**Rows:** 0 (optional feature)  
**Loaded from:** FBRef CSV files

| Column | Type | Description |
|--------|------|-------------|
| `player_name` | VARCHAR(255) | Player name |
| `team_name` | VARCHAR(255) | Team name |
| `minutes_played` | INT | Minutes player was on field |
| `goals` | INT | Goals scored |
| `assists` | INT | Assists provided |
| `xg` | DECIMAL(6,2) | Expected goals (xG) |
| `xa` | DECIMAL(6,2) | Expected assists (xA) |
| `yellow_cards` | INT | Yellow cards received |
| `red_cards` | INT | Red cards received |
| `shots` | INT | Total shots |
| `shots_on_target` | INT | Shots on target |
| `season_label` | VARCHAR(9) | Season label (e.g., '2023/24') |
| `load_timestamp` | DATETIME | Load timestamp |

---

## 6. stg_referee_raw (Referee Staging)

**Purpose:** Intermediate staging for referee data  
**Rows:** ~150  
**Loaded from:** Manual CSV upload

| Column | Type | Description |
|--------|------|-------------|
| `referee_id` | INT | PK - Auto-increment |
| `file_name` | VARCHAR(255) | Source file name |
| `load_start_time` | DATETIME | Load start timestamp |
| `load_end_time` | DATETIME | Load end timestamp |
| `status` | VARCHAR(20) | Load status |
| `rows_processed` | INT | Count of rows processed |
| `error_message` | TEXT | Error details |
| `created_at` | DATETIME | Row creation timestamp |
| `referee_name` | VARCHAR(255) | Referee name |
| `date_of_birth` | DATE | Birth date |
| `nationality` | VARCHAR(100) | Nationality |
| `premier_league_debut` | DATE | First EPL match date |
| `ref_status` | VARCHAR(50) | Status (ACTIVE, RETIRED, etc.) |
| `notes` | TEXT | Additional notes |

**Indexes:**
- `PRIMARY KEY (referee_id)`
- `INDEX idx_file_name (file_name)`
- `INDEX idx_status (status)`

---

# 📋 ETL METADATA TABLES

## 1. etl_log (ETL Execution Log)

**Purpose:** Track all ETL job executions and phases  
**Rows:** ~1000+ (grows with each execution)

| Column | Type | Description |
|--------|------|-------------|
| `log_id` | INT | PK - Auto-increment |
| `job_name` | VARCHAR(100) | Name of ETL job (e.g., 'staging', 'warehouse') |
| `phase_step` | VARCHAR(100) | Phase/step name (e.g., 'load_events_step1') |
| `status` | VARCHAR(20) | Status (STARTED, RUNNING, COMPLETED, FAILED) |
| `start_time` | DATETIME | When phase started |
| `end_time` | DATETIME | When phase ended |
| `rows_processed` | INT | Number of rows processed |
| `message` | TEXT | Status message or error details |
| `created_at` | DATETIME | When log entry was created |

**Sample Rows:**
```
log_id | job_name | phase_step                | status    | rows_processed | message
────────────────────────────────────────────────────────────────────────────────────
1      | staging  | load_csv_matches          | COMPLETED | 830            | OK
2      | staging  | load_statsbomb_events     | COMPLETED | 1362577        | OK
3      | warehouse| dim_team                  | COMPLETED | 31             | OK
4      | warehouse| fact_match                | COMPLETED | 830            | OK
5      | warehouse| fact_match_events_step1   | COMPLETED | 1362577        | OK
```

---

## 2. etl_file_manifest (CSV File Load Tracking)

**Purpose:** Track which CSV files have been loaded  
**Rows:** ~50+

| Column | Type | Description |
|--------|------|-------------|
| `file_id` | INT | PK - Auto-increment |
| `file_name` | VARCHAR(255) | File name (UNIQUE) |
| `league_div` | VARCHAR(5) | League division (E0, E1, E2, etc.) |
| `load_start_time` | DATETIME | Load start timestamp |
| `load_end_time` | DATETIME | Load end timestamp |
| `status` | VARCHAR(20) | Load status |
| `rows_processed` | INT | Count of rows processed |
| `error_message` | TEXT | Error details if failed |
| `created_at` | DATETIME | Row creation timestamp |

---

## 3. etl_api_manifest (API Call Tracking)

**Purpose:** Track API calls and their results  
**Rows:** ~100+

| Column | Type | Description |
|--------|------|-------------|
| `api_id` | INT | PK - Auto-increment |
| `api_name` | VARCHAR(255) | API name (e.g., 'FootballData.org') |
| `endpoint` | VARCHAR(255) | API endpoint |
| `season` | INT | Season year |
| `load_start_time` | DATETIME | Call start timestamp |
| `load_end_time` | DATETIME | Call end timestamp |
| `status` | VARCHAR(20) | Call status |
| `rows_processed` | INT | Rows received |
| `error_message` | TEXT | Error details if failed |
| `created_at` | DATETIME | Row creation timestamp |

**Unique Key:**
```sql
UNIQUE KEY uk_api_call (api_name, endpoint, season)
```

---

# 📊 ADDITIONAL METADATA TABLES

## 4. etl_excel_manifest (Excel File Tracking)
## 5. etl_json_manifest (JSON File Tracking)
## 6. etl_events_manifest (Events File Tracking)

These tables follow similar structure for tracking loads from Excel, JSON, and event files.

---

# 🔍 Table Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DIMENSION TABLES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  dim_date ◄────┐                    ┌────► dim_season              │
│  (17.5K rows)  │                    │      (9 rows)                │
│                │                    │                              │
│  dim_team ◄────┤                    │      dim_player              │
│  (31 rows)     │                    │      (6.8K rows)             │
│       ▲        │                    │           ▲                  │
│       │        │                    │           │                  │
│       │        │  ┌─────────────────┼───────────┼────┐             │
│       │        │  │                 │           │    │             │
│       │        │  │                 │           │    │             │
│  fact_match ◄──┴──┤      referee_id │ stadium_id│    │             │
│  (830 rows)      │      (-1/NULL)   │ (-1/NULL) │    │             │
│       ▲          │                  │          │    │             │
│       │          │  dim_referee ◄───┘  dim_stadium   │             │
│       │          │  (33 rows)         (58 rows)      │             │
│       │          │                                   │             │
│       │          └──────────────────────────────────┘             │
│       │                                                            │
│  fact_match_events ────► (1.36M events)                           │
│       │                                                            │
│  fact_player_stats ────► (0 rows, optional)                       │
│                                                                    │
│  MAPPING TABLES:                                                  │
│  ├─ dim_team_mapping (40 rows) ──────────────────► StatsBomb IDs │
│  └─ dim_match_mapping (684 rows) ─────────────────► StatsBomb IDs │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘

                    ▼
        ┌──────────────────────────┐
        │  STAGING TABLES (TEMP)   │
        ├──────────────────────────┤
        │ stg_e0_match_raw (830)   │
        │ stg_events_raw (1.3M)    │
        │ stg_team_raw (~600)      │
        │ stg_player_raw (~7K)     │
        │ stg_referee_raw (~150)   │
        │ stg_player_stats_fbref   │
        │    (0, optional)         │
        └──────────────────────────┘

                    ▼
        ┌──────────────────────────┐
        │   ETL METADATA TABLES    │
        ├──────────────────────────┤
        │ etl_log                  │
        │ etl_file_manifest        │
        │ etl_api_manifest         │
        │ etl_json_manifest        │
        │ etl_events_manifest      │
        │ etl_excel_manifest       │
        └──────────────────────────┘
```

---

# 📈 Data Volumes

| Table | Rows | Purpose | Growth |
|-------|------|---------|--------|
| **dim_date** | 17,533 | Calendar | ~365/year |
| **dim_team** | 31 | Teams | Static (~20 EPL teams) |
| **dim_player** | 6,809 | Players | ~500-1000/season |
| **dim_referee** | 33 | Referees | ~30-40 Static |
| **dim_stadium** | 58 | Stadiums | Static (~40-50) |
| **dim_season** | 9 | Seasons | +1/year |
| **fact_match** | 830 | Matches | ~380/season (EPL) |
| **fact_match_events** | 1,362,577 | Events | ~1.3-1.5M/season |
| **fact_player_stats** | 0 | Player stats | Optional |
| **dim_team_mapping** | 40 | Team bridge | Static |
| **dim_match_mapping** | 684 | Match bridge | ~380-400/season |
| **Staging tables** | ~2M | Temporary | Cleared after load |
| **ETL metadata** | ~1K+ | Audit trail | +1 per execution |

**Total Current Size:** ~1.4M rows in production tables

---

# 🔑 Key Constraints & Validations

## Primary Keys (All Tables)
- Surrogate keys on all dimensions
- Auto-increment for dimensions
- Business keys on staging/mapping tables

## Foreign Keys (Fact Tables)
- `fact_match` → all 6 dimensions
- `fact_match_events` → `fact_match`, `dim_player`, `dim_team`
- `fact_player_stats` → `fact_match`, `dim_player`, `dim_team`

## Check Constraints
- `fact_match.home_goals BETWEEN 0 AND 20`
- `fact_match.away_goals BETWEEN 0 AND 20`

## Unique Keys
- `dim_team.team_code`, `dim_team.team_name`
- `dim_player.player_bk`, `dim_player.external_id`
- `stg_e0_match_raw.match_source_key`
- `etl_api_manifest (api_name, endpoint, season)`

## Sentinel/Default Values
- `-1` for UNKNOWN dimension rows (safety net for FK constraints)
- `DEFAULT CURRENT_TIMESTAMP` on all `created_at` columns

---

# 📊 Query Examples

## Count rows in each table
```sql
SELECT 'dim_date' AS tbl, COUNT(*) FROM dim_date
UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL SELECT 'dim_player', COUNT(*) FROM dim_player
UNION ALL SELECT 'fact_match', COUNT(*) FROM fact_match
UNION ALL SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
ORDER BY tbl;
```

## Top 10 matches by event count
```sql
SELECT fm.match_id, 
       dt1.team_name AS home_team,
       dt2.team_name AS away_team,
       fm.home_goals, fm.away_goals,
       COUNT(*) AS event_count
FROM fact_match fm
LEFT JOIN dim_team dt1 ON fm.home_team_id = dt1.team_id
LEFT JOIN dim_team dt2 ON fm.away_team_id = dt2.team_id
LEFT JOIN fact_match_events fme ON fm.match_id = fme.match_id
GROUP BY fm.match_id
ORDER BY event_count DESC
LIMIT 10;
```

## Top scorers
```sql
SELECT 
    dp.player_name,
    dt.team_name,
    COUNT(*) AS goal_events
FROM fact_match_events fme
LEFT JOIN dim_player dp ON fme.player_id = dp.player_id
LEFT JOIN dim_team dt ON fme.team_id = dt.team_id
WHERE fme.event_type = 'Goal'
GROUP BY dp.player_name, dt.team_name
ORDER BY goal_events DESC
LIMIT 10;
```

---

## References

- **Full Pipeline Guide:** See `ETL_PIPELINE_GUIDE.md`
- **Fact Loading Details:** See `LOAD_FACT_TABLES_GUIDE.md`
- **SQL Scripts Reference:** See `SQL_SCRIPTS_REFERENCE.md`
- **Main Source:** `src/sql/create_schema.sql`

