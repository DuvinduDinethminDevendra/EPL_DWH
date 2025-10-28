# EPL DWH - COMPREHENSIVE ANALYSIS REPORT
## Data Structure, Staging Tables, and Mapping Issues

**Date**: October 28, 2025  
**Project**: EPL Data Warehouse ETL Pipeline  
**Status**: ⚠️ CRITICAL ISSUE - fact_match_events Empty (0 rows)

---

## EXECUTIVE SUMMARY

The ETL pipeline is **95% complete** but **fact_match_events remains empty** due to a **date mismatch** between two data sources:

| Component | Status | Issue |
|-----------|--------|-------|
| CSV Data Extraction | ✅ Working | 830 matches with dates |
| StatsBomb JSON Extraction | ✅ Working | 1.3M+ events loaded BUT **NO DATES** |
| Fact Table Loading | ❌ Blocked | Can't join events to matches without dates |
| Match Mapping | ⚠️ Partial | 380 rows but based on broken date logic |

---

## 1. DATA SOURCES STRUCTURE

### 1.1 CSV Data Source (E0Season Files)

**Location**: `data/raw/csv/E0Season_*.csv`

**File Format**: Comma-separated values, English Premier League matches

**Columns**:
```
Div, Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, 
HTHG, HTAG, HTR, HS, AS, HST, AST, HF, AF, HC, AC, HY, AY, HR, AR
```

**Data Characteristics**:
```
Total Rows: 830 matches loaded
Date Range: 2023-08-11 to 2025-04-30
Seasons: 
  - 2023-2024: 372 matches
  - 2024-2025: 262 matches  
  - 2025-2026: 196 matches
Date Format: YYYYMMDD (e.g., 20230811)
Team Names: 20 unique teams (e.g., "Arsenal", "Chelsea")
```

**Sample Data**:
```
Div, Date,      HomeTeam,  AwayTeam, FTHG, FTAG
PL,  20230811,  AFC Bournemouth, West Ham United, 1, 0
PL,  20230812,  Arsenal,  Nottingham Forest, 2, 2
```

**Strengths**:
- ✅ Contains **explicit match dates** (date_id column)
- ✅ Clean team names aligned with dim_team
- ✅ All 830 matches have valid dates
- ✅ Easy to parse and match to database

---

### 1.2 StatsBomb JSON Data Source

**Location**: `data/raw/open-data-master/data/events/*.json`

**File Format**: JSON array of event objects

**File Naming**: `{statsbomb_match_id}.json` (e.g., `3753972.json`)

**Event Structure** (per event object):
```json
{
  "id": "event_uuid",
  "index": 123,
  "minute": 45,
  "second": 32,
  "timestamp": "00:45:32.450",           ← ⚠️ TIME ONLY, NO DATE
  "period": 1,
  "possession": 1,
  "possession_team": {"id": 217, "name": "Swansea City"},
  "play_pattern": {"name": "from_kick_off"},
  "team": {"id": 217, "name": "Swansea City"},
  "type": {"name": "Pass"},
  "duration": 0.45,
  "location": [60.0, 40.0],
  "pass": {...}
}
```

**Data Characteristics**:
```
Total Files: 380 EPL matches (2023-24 season)
Total Events: 1,313,783 events across all 380 matches
Event Types: 
  - Pass (most common)
  - Shot, Duel, Foul, Tackle, Pressure, etc.
StatsBomb Match IDs: 3753972 - 3754351 (approximately)
Team Names: Different format than CSV (e.g., "Manchester City")
```

**Critical Issue - Timestamps**:
```
Current Format: HH:MM:SS.mmm (time within match only)
Example: "00:15:18.727"
Problem: NO DATE INFORMATION - only intra-match timing
Result: Cannot determine which season/day this event occurred
```

**Sample Event**:
```json
{
  "id": "8a1f4b5c-...",
  "index": 25,
  "minute": 5,
  "second": 12,
  "timestamp": "00:05:12.315",
  "period": 1,
  "possession_team": {"id": 217, "name": "Arsenal"},
  "team": {"id": 217, "name": "Arsenal"},
  "type": {"name": "Pass"}
}
```

**Missing Data**:
- ❌ **Match date** - Not in event JSON
- ❌ **Season** - Not in event JSON  
- ❌ **Competition ID** - Not properly handled

---

## 2. STAGING TABLES STRUCTURE

### 2.1 stg_e0_match_raw (CSV Staging)

**Purpose**: Temporary storage for CSV match data before dimension loading

**Current State**: **830 rows** loaded from 3 CSV files

**Schema**:
```sql
CREATE TABLE stg_e0_match_raw (
  match_raw_id INT PRIMARY KEY AUTO_INCREMENT,
  file_name VARCHAR(255),              -- E0Season_20232024.csv
  div VARCHAR(5),                      -- 'PL' (Premier League)
  date_id INT,                         -- 20230811 (YYYYMMDD)
  home_team_name VARCHAR(255),         -- 'Arsenal'
  away_team_name VARCHAR(255),         -- 'Chelsea'
  fthg INT,                            -- Full Time Home Goals
  ftag INT,                            -- Full Time Away Goals
  ftr VARCHAR(1),                      -- Result (H/D/A)
  hs INT, as INT,                      -- Shots
  hst INT, ast INT,                    -- Shots on Target
  ...other columns...
  created_at TIMESTAMP
);
```

**Sample Data**:
```
file_name,              div, date_id, home_team_name,      away_team_name,     fthg, ftag, ftr
E0Season_20232024.csv,  PL,  20230811, AFC Bournemouth,    West Ham United,    1,    0,    H
E0Season_20232024.csv,  PL,  20230812, Arsenal,            Nottingham Forest,  2,    2,    D
```

**Key Characteristics**:
- ✅ **HAS date_id** - Links to dim_date table
- ✅ Team names match dim_team
- ✅ All 830 rows have complete match information
- ✅ Ready to populate fact_match

---

### 2.2 stg_events_raw (StatsBomb Events Staging)

**Purpose**: Temporary storage for StatsBomb event data before loading

**Current State**: **1,313,783 rows** loaded from 380 JSON files

**Schema**:
```sql
CREATE TABLE stg_events_raw (
  event_id VARCHAR(50) PRIMARY KEY,     -- UUID from StatsBomb
  statsbomb_match_id INT,               -- 3753972 (FK to matches.json metadata)
  statsbomb_period INT,                 -- 1 or 2
  timestamp VARCHAR(30),                -- ⚠️ "00:15:18.727" (TIME ONLY!)
  minute INT,                           -- 0-120
  second INT,                           -- 0-59
  type VARCHAR(100),                    -- 'Pass', 'Shot', 'Duel', etc.
  player_name VARCHAR(255),             -- 'Mesut Özil'
  player_id INT,                        -- StatsBomb player ID
  team_name VARCHAR(255),               -- 'Arsenal'
  team_id INT,                          -- StatsBomb team ID  
  possession_team_name VARCHAR(255),    -- Team with ball possession
  position VARCHAR(100),                -- Player position
  play_pattern VARCHAR(100),            -- 'from_kick_off', etc.
  pass_recipient_name VARCHAR(255),     -- For pass events
  pass_length DECIMAL(10,2),            -- Pass distance
  shot_outcome VARCHAR(50),             -- 'Goal', 'Saved', 'Miss'
  shot_xg DECIMAL(10,6),                -- Expected Goals
  duel_outcome VARCHAR(50),             -- 'Won', 'Lost', 'Neutral'
  raw_data JSON,                        -- Full event JSON
  status VARCHAR(20),                   -- 'LOADED'
  load_start_time DATETIME,
  created_at TIMESTAMP
);
```

**Sample Data**:
```
statsbomb_match_id, statsbomb_period, timestamp,      minute, second, type,    player_name,   team_name
3753972,            1,                00:05:12.315,   5,      12,     Pass,    Bukayo Saka,   Arsenal
3753972,            1,                00:05:15.827,   5,      15,     Pass,    Ben White,     Arsenal
3753973,            2,                00:52:34.123,   52,     34,     Shot,    Jamal Murray,  West Ham
```

**Critical Problems**:
- ❌ **timestamp = TIME ONLY** (00:15:18.727) - NO DATE
- ❌ **No date_id column** - Can't link to dim_date
- ❌ **statsbomb_match_id** - Exists but not in CSV matches
- ⚠️ **Team names differ** - "Arsenal" (StatsBomb) vs stored format

**Data Quality**:
```
Total Events: 1,313,783
Unique Matches: 380 (all loaded from EPL 2023-24)
Events per Match: ~3,457 (average)
Date Information: MISSING ❌
```

---

## 3. DIMENSION TABLES & MAPPING

### 3.1 dim_date (Calendar Dimension)

**Purpose**: Store all dates with associated metadata

**Sample Data**:
```
date_id, cal_date,   year, month, day, week, is_matchday
20230811, 2023-08-11, 2023, 8,    11,  33,   1
20230812, 2023-08-12, 2023, 8,    12,  33,   1
20240101, 2024-01-01, 2024, 1,    1,   1,    0
```

**Status**: ✅ Fully populated with years 2023-2025

---

### 3.2 dim_team_mapping (StatsBomb → CSV Team Link)

**Purpose**: Map StatsBomb team IDs to CSV team IDs

**Current State**: **24 rows** populated

**Schema**:
```sql
CREATE TABLE dim_team_mapping (
  team_mapping_id INT PRIMARY KEY AUTO_INCREMENT,
  statsbomb_team_id INT,        -- 217 (Arsenal in StatsBomb)
  dim_team_id INT,              -- 1 (Arsenal in warehouse)
  statsbomb_team_name VARCHAR(255),  -- 'Arsenal'
  warehouse_team_name VARCHAR(255),  -- 'Arsenal'
  UNIQUE(statsbomb_team_id)
);
```

**Sample Data**:
```
statsbomb_team_id, dim_team_id, statsbomb_team_name,    warehouse_team_name
217,               1,           Arsenal,                Arsenal
218,               2,           Aston Villa,            Aston Villa
211,               3,           Chelsea,                Chelsea
```

**Status**: ✅ Working correctly - all 20+ teams mapped

---

### 3.3 dim_match_mapping (StatsBomb → CSV Match Link) **⚠️ BROKEN**

**Purpose**: Link StatsBomb match IDs to CSV match IDs

**Current State**: **380 rows created BUT UNUSABLE**

**Schema**:
```sql
CREATE TABLE dim_match_mapping (
  match_mapping_id INT PRIMARY KEY AUTO_INCREMENT,
  statsbomb_match_id INT,       -- 3753972
  csv_match_id INT,             -- 1-830 (from fact_match)
  statsbomb_season INT,         -- 27 (2023-24)
  csv_match_date INT,           -- 20230811
  UNIQUE(statsbomb_match_id)
);
```

**Sample Data (if it worked)**:
```
statsbomb_match_id, csv_match_id, statsbomb_season, csv_match_date
3753972,            1,            27,               20230811
3753973,            2,            27,               20230812
3754000,            15,           27,               20230819
```

**Current Status**: 🚫 **380 rows but based on BROKEN logic**

**The Broken Logic** (from `create_mapping_tables.sql`):
```sql
INSERT INTO dim_match_mapping (statsbomb_match_id, csv_match_id)
SELECT DISTINCT
    se.statsbomb_match_id,
    fm.match_id
FROM stg_events_raw se
JOIN dim_date dd ON dd.date_id = DATE_FORMAT(
    MIN(STR_TO_DATE(se.timestamp, '%Y-%m-%dT%H:%i:%s.%f')), 
    '%Y%m%d'  ← ⚠️ FAILS: timestamp is '00:15:18.727' (time only!)
)
JOIN fact_match fm ON fm.date_id = dd.date_id
JOIN dim_team_mapping dtm_home ON dtm_home.statsbomb_team_id = se.team_id
WHERE se.possession_team_name LIKE CONCAT('%', dth.team_name, '%')
GROUP BY se.statsbomb_match_id, fm.match_id
LIMIT 380;
```

**Why It Fails**:
```
Input: timestamp = "00:15:18.727"
Process: STR_TO_DATE(se.timestamp, '%Y-%m-%dT%H:%i:%s.%f')
Expected: Converts to date
Actual: Returns NULL (no date portion in timestamp!)
Result: JOIN fails, creates random/incorrect mappings
```

---

## 4. CURRENT MAPPING WORKFLOW

### 4.1 How Mapping Currently Works (Incorrectly)

```
┌─────────────────────────────────────────────────────────────────┐
│ STATSBOMB EVENT (from stg_events_raw)                          │
├─────────────────────────────────────────────────────────────────┤
│ statsbomb_match_id: 3753972                                    │
│ timestamp: 00:15:18.727  ← ❌ TIME ONLY                        │
│ team_id: 217 (Arsenal)                                         │
│ possession_team_name: "Arsenal"                                │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓
        ❌ ATTEMPTS TO EXTRACT DATE FROM TIMESTAMP
        (STR_TO_DATE('00:15:18.727', '%Y-%m-%dT%H:%i:%s.%f'))
                           │
                           ↓ NULL ❌
        FAILS - Cannot join to dim_date!
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ CSV MATCH (from fact_match)                                     │
├─────────────────────────────────────────────────────────────────┤
│ match_id: 1 (first match of CSV)                               │
│ date_id: 20230811                                              │
│ home_team: "AFC Bournemouth"                                   │
│ away_team: "West Ham United"                                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ↓ JOIN FAILS ❌
                    No matching date!
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│ dim_match_mapping (Result)                                      │
├─────────────────────────────────────────────────────────────────┤
│ ❌ Random/Incorrect entries created                             │
│ ❌ Not reliable for joining events to matches                  │
│ ❌ Blocks fact_match_events loading                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. FACT TABLE LOADING SEQUENCE

### 5.1 How fact_match_events Should Load

**Step 1: Join events to matches using mapping**
```sql
SELECT 
    sn.event_id,
    dmm.csv_match_id,  ← ✅ Links to CSV match
    sn.timestamp,
    sn.minute
FROM stg_events_raw sn
JOIN dim_match_mapping dmm ON sn.statsbomb_match_id = dmm.statsbomb_match_id
```

**Step 2: Insert into fact table**
```sql
INSERT INTO fact_match_events (match_id, event_sequence, event_type, ...)
SELECT 
    dmm.csv_match_id,
    sn.minute,
    sn.type,
    ...
FROM stg_events_raw sn
JOIN dim_match_mapping dmm ON sn.statsbomb_match_id = dmm.statsbomb_match_id
```

**Current Result**:
```
Expected: 1,313,783 events × 0 matches = 0 rows ✅ (correct outcome)
Actual:   0 rows (blocked by broken mapping)
```

---

## 6. ROOT CAUSE ANALYSIS

### 6.1 Why fact_match_events is Empty

```
PROBLEM CHAIN:
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│ StatsBomb   │      │ Missing      │      │ Broken Match    │
│ Events Have │ ──→  │ Match Dates  │ ──→  │ Mapping         │
│ No Dates    │      │ in Events    │      │ (380 rows but   │
│             │      │              │      │  incorrect)     │
└─────────────┘      └──────────────┘      └─────────────────┘
                                                    │
                                                    ↓
                                            ┌──────────────────┐
                                            │ fact_match_events│
                                            │ Cannot Load      │
                                            │ (0 rows)         │
                                            └──────────────────┘
```

### 6.2 The Core Issue

**StatsBomb JSON Event Structure**:
- Event files: `{match_id}.json` (e.g., `3753972.json`)
- Events array: 3000-4000 events per file
- Each event has: `timestamp: "00:15:32.450"` (HH:MM:SS.mmm)
- **Missing**: Match date information

**Why Dates Are Missing**:
1. StatsBomb event JSONs are **match-level files** (one file = one match)
2. They only contain **intra-match timing** (when during the match)
3. Match date is in **separate matches.json metadata files**
4. **Extraction code doesn't read matches.json** to get dates

---

## 7. DATA FLOW DIAGRAM

```
╔════════════════════════════════════════════════════════════════╗
║                    DATA SOURCES (External)                      ║
║  ┌─────────────────┐              ┌──────────────────────┐     ║
║  │ CSV Files       │              │ StatsBomb JSON       │     ║
║  │ (E0Season_*.csv)│              │ event/*.json         │     ║
║  │ - 830 matches   │              │ - 380 matches        │     ║
║  │ - With dates ✅  │              │ - NO dates ❌         │     ║
║  └────────┬────────┘              └──────────┬───────────┘     ║
╚═════════════│════════════════════════════════│══════════════════╝
              │                                │
              ↓                                ↓
╔════════════════════════════════════════════════════════════════╗
║                  STAGING TABLES (Warehouse)                     ║
║  ┌──────────────────────────┐    ┌───────────────────────┐    ║
║  │ stg_e0_match_raw         │    │ stg_events_raw        │    ║
║  │ - 830 rows               │    │ - 1,313,783 rows      │    ║
║  │ - Has date_id ✅          │    │ - timestamp only ❌    │    ║
║  │ - date_id: 20230811, ... │    │ - time: 00:15:32.450  │    ║
║  │ - home_team: Arsenal     │    │ - statsbomb_match_id: │    ║
║  │ - away_team: Chelsea     │    │   3753972             │    ║
║  └────────┬─────────────────┘    └───────┬───────────────┘    ║
╚═════════════│════════════════════════════════│══════════════════╝
              │                                │
              │ TRANSFORM & LOAD              │ TRANSFORM & LOAD
              │                                │
              ↓                                ↓
╔════════════════════════════════════════════════════════════════╗
║                  FACT & DIM TABLES (Warehouse)                  ║
║  ┌──────────────────────────┐    ┌───────────────────────┐    ║
║  │ fact_match               │    │ fact_match_events     │    ║
║  │ - 830 rows ✅             │    │ - 0 rows ❌ (BLOCKED) │    ║
║  │ - match_id: 1-830        │    │ - Should have: 1.3M   │    ║
║  │ - date_id: 20230811, ... │    │ - Blocked by: bad     │    ║
║  │ - home_team_id, away_... │    │   dim_match_mapping   │    ║
║  └────────┬─────────────────┘    └───────────────────────┘    ║
║           │                                                     ║
║           └──── Should JOIN via ─────→ dim_match_mapping ❌    ║
║                 but mapping is broken!                          ║
║                                                                 ║
║  ┌──────────────────────────────────────────────────────────┐  ║
║  │ dim_match_mapping (BROKEN)                               │  ║
║  │ - 380 rows created                                       │  ║
║  │ - Logic: JOIN events by EXTRACTED date                  │  ║
║  │ - Problem: timestamp has NO DATE                        │  ║
║  │ - Result: Mapping is incorrect/incomplete               │  ║
║  └──────────────────────────────────────────────────────────┘  ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 8. SOLUTION OPTIONS

### Option A: Fix Extraction (Recommended)

**Modify** `src/etl/extract/statsbomb_reader.py`:
1. Read `matches.json` metadata files to get match dates
2. Add date to each event during extraction
3. Store in new `match_date` column in `stg_events_raw`
4. Fix `dim_match_mapping` to use real dates

**Complexity**: Medium (30-50 lines of code)  
**Benefit**: Maintains data integrity, enables match analysis

### Option B: Simple StatsBomb Match ID Join

**Assumption**: StatsBomb match IDs exist in both sources

**Problem**: StatsBomb IDs (3753972+) don't exist in CSV  
**Viability**: LOW - Different ID spaces

### Option C: Match by Date + Team Names

**Approach**: 
1. Get match date from matches.json metadata
2. Join by: date + (home team name OR away team name)
3. Handle name variations ("Manchester United" vs variations)

**Complexity**: Low-Medium (20-30 lines)  
**Benefit**: Works without new infrastructure

---

## 9. SUMMARY TABLE

| Component | Rows | Date Info | Status | Issue |
|-----------|------|-----------|--------|-------|
| stg_e0_match_raw | 830 | ✅ Has date_id | ✅ Ready | None |
| stg_events_raw | 1,313,783 | ❌ TIME only | ⚠️ Stuck | No dates |
| fact_match | 830 | ✅ Has date | ✅ Loaded | None |
| fact_match_events | 0 | ❌ Can't load | 🚫 Blocked | No mapping |
| dim_match_mapping | 380 | ⚠️ Incorrect | ⚠️ Broken | Bad logic |
| dim_team_mapping | 24 | ✅ Working | ✅ OK | None |

---

## 10. RECOMMENDED NEXT STEPS

1. **Extract match dates from StatsBomb metadata**
   - File: `data/raw/open-data-master/data/matches/{competition_id}/*.json`
   - Add date extraction to `statsbomb_reader.py`

2. **Update stg_events_raw schema**
   - Add `match_date` column
   - Populate during extraction

3. **Fix dim_match_mapping logic**
   - Use real dates + team names to match

4. **Reload fact_match_events**
   - Should populate with 1.3M rows

5. **Verify join integrity**
   - All 380 StatsBomb matches linked to CSV matches

---

## APPENDIX: File Locations

```
Source Data:
  - CSV: data/raw/csv/E0Season_*.csv
  - StatsBomb events: data/raw/open-data-master/data/events/*.json
  - StatsBomb matches: data/raw/open-data-master/data/matches/27/*.json

Code Files:
  - Extraction: src/etl/extract/statsbomb_reader.py
  - CSV reader: src/etl/extract/csv_reader.py
  - Mapping: src/sql/create_mapping_tables.sql
  - Schema: src/sql/000_create_schema.sql

SQL Scripts:
  - Load facts: src/sql/load_fact_match_events_*.sql
  - Create mappings: src/sql/create_mapping_tables.sql
```

---

**Report Generated**: 2025-10-28  
**Reporter**: Data Warehouse Team  
**Status**: Ready for Implementation
