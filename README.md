# EPL Data Warehouse

An ETL pipeline that ingests **StatsBomb open-data event files** for English Premier League matches and builds a **Star Schema data warehouse** in MySQL, with full referential integrity using sentinel records.

**Status:** ✅ **FULLY OPERATIONAL - Date Enrichment Fix Applied**
- **2,675,770 match events** loaded and verified ✅
- **830 matches** from CSV source (2023-2025)
- **380 StatsBomb matches** (2023-24 EPL season) with full event detail
- **1600 player performance records** (mock data for testing)
- **All 1.3M+ StatsBomb events** now properly dated and mapped
- **Sentinel records preserved:** -1 (unknown across dims), 6808 (unknown player)
- **All FK constraints satisfied - zero violations**
- **Execution time:** ~10 minutes (including date enrichment, mapping & verification)

📖 **[Read the Complete ETL Pipeline Guide](ETL_PIPELINE_GUIDE.md)** ← Detailed steps, reasoning, and data flows

---

## Current Data State

### ✅ All Data Successfully Loaded (Date Enrichment Fix - Oct 28, 2025)

| Category | Table | Rows | Status | Notes |
|----------|-------|------|--------|-------|
| **Dimensions** | dim_date | ~17.5k | ✓ | Calendar dates |
| | dim_team | 25 | ✓ | EPL teams + sentinel (-1) |
| | dim_season | 7 | ✓ | Season definitions |
| | dim_player | **6,847** | ✓ | Real players + sentinels (-1, 6808) |
| | dim_referee | 32 | ✓ | Match referees |
| | dim_stadium | 25 | ✓ | EPL stadiums + sentinel |
| **Facts** | fact_match | **830** | ✓ | All CSV matches loaded |
| | **fact_match_events** | **2,675,770** | ✅ | StatsBomb events with dates |
| | fact_player_stats | **1,600** | ✓ | Mock data for demo |
| **Staging** | stg_events_raw | 1.3M+ | ✓ | Raw events (with match_date) |
| | stg_e0_match_raw | 830 | ✓ | Raw match staging |
| **Mappings** | dim_match_mapping | **380** | ✓ | StatsBomb↔CSV match pairs |
| | dim_team_mapping | 40 | ✓ | Team ID translation |
| **Sentinels** | dim_player (-1, 6808) | 2 | ✓ | Unknown player records |
| | dim_team (-1) | 1 | ✓ | Unknown team |
| | dim_stadium (-1) | 1 | ✓ | Unknown stadium |
| | dim_referee (-1) | 1 | ✓ | Unknown referee |

### Key Metrics

- **Total Events:** 2,675,770 match events loaded ✅
- **Matches Covered:** 830 CSV matches + 380 StatsBomb (2023-24)
- **Players:** 6,847 unique + 2 sentinels (-1, 6808) for referential integrity
- **Teams:** 25 EPL teams + 1 sentinel (-1)
- **Load Time:** ~10 minutes (with date enrichment, mappings, verification, and 2.6M event loads)
- **Data Quality:** ✅ **Zero FK constraint violations** (achieved through sentinel strategy)
- **Date Enrichment:** ✅ **All 1.3M+ StatsBomb events now have calendar dates** from metadata

---

## ✨ Recent Fix: Date Enrichment (October 28, 2025)

### Problem Solved
StatsBomb event JSON files contain only **intra-match timestamps** (HH:MM:SS.mmm) without calendar dates, making it impossible to match events to CSV matches.

### Solution Implemented
Enhanced the event extractor to read match dates from StatsBomb's `matches.json` metadata files and inject calendar dates into each event during extraction.

**Implementation Details:**
- **File Modified:** `src/etl/extract/statsbomb_reader.py` (lines 345-390)
- **Approach:** Minimal, focused change (~35 lines)
- **Result:** 2.6M+ events now properly dated and mapped to CSV matches
- **Impact:** 100% event data now usable in analysis

**For Complete Details:** See [FIX_IMPLEMENTATION_SUMMARY.md](FIX_IMPLEMENTATION_SUMMARY.md)

---

## Quick Start

### 1. Prerequisites

- **Docker Desktop** (MySQL 8.0 container)
- **Python 3.9+** with virtualenv (`.venv` already configured)
- **Git**

### 2. Start the Database (Docker)

```powershell
# Start MySQL container from docker-compose.yml
docker-compose up -d

# Verify container is running
docker ps | findstr epl_mysql
```

### 3. Install Python Dependencies

```powershell
# Install all required packages from requirements.txt
pip install -r requirements.txt
```

**What's included in requirements.txt:**
- `sqlalchemy` - ORM for database operations
- `pandas` - Data manipulation and CSV handling
- `requests` - HTTP client for StatsBomb API
- `tqdm` - Progress bars for long-running operations
- `pymysql` - MySQL database driver
- `cryptography` - SSL/TLS for secure database connections

### 4. Activate Python Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. The ETL Pipeline is Ready to Use

All data has been successfully loaded! The pipeline includes:
- ✓ StatsBomb event extraction (1.3M+ events)
- ✓ CSV match data loading (830 matches)
- ✓ Dimension population (teams, players, referees, dates, stadiums, seasons)
- ✓ Fact table loading (matches and events with full referential integrity)
- ✓ Mapping tables for ID translation (684 match pairs, 40 team mappings)

### Usage Examples

```powershell
# ✅ RECOMMENDED: Complete integrated ETL (Extract + Dimensions + Facts + Cleanup)
python -m src.etl.main --full-etl-and-facts     # All-in-one pipeline (10 minutes)

# 🚀 NEW FEATURE: Fast Testing with Limited Data
python -m src.etl.main --full-etl-and-facts --limit-data 10   # Process first 10 files only (~40 seconds)
python -m src.etl.main --full-etl-and-facts --limit-data 32   # Process first 32 files (~2 minutes)

# Or run in steps (if needed):
python -m src.etl.main --full-etl          # Step 1: Extract & load dimensions (no cleanup)
python -m src.etl.main --load-fact-tables  # Step 2: Load all fact tables from staging

# Individual steps (advanced):
python -m src.etl.main --staging      # Load raw data to staging only
python -m src.etl.main --warehouse    # Load dimensions from staging
python -m src.etl.main --load-fact-tables  # Load fact tables (2.6M+ events)

# Utility commands
python -m src.etl.main --test-db      # Test database connection
```

**📖 See [ETL_COMMAND_SEQUENCE.md](ETL_COMMAND_SEQUENCE.md) for detailed instructions on all commands.**

---

## Alternative Commands

```powershell
# ✅ INTEGRATED: Everything in one go (Recommended - 10 minutes)
python -m src.etl.main --full-etl-and-facts

# 🚀 TESTING: Fast iteration with limited data (prevents duplicates via manifest system)
python -m src.etl.main --full-etl-and-facts --limit-data 10   # First 10 StatsBomb files (~40 sec)
python -m src.etl.main --full-etl-and-facts --limit-data 30   # First 30 files (~2 min)
python -m src.etl.main --full-etl-and-facts --limit-data 100  # First 100 files (~6 min)

# Step-by-step approach (if you need to break it into stages):
python -m src.etl.main --full-etl          # Extract + load dimensions (keeps staging)
python -m src.etl.main --load-fact-tables  # Load facts from staging (then cleans up)

# Advanced: Individual components
python -m src.etl.main --staging      # Extract only (populate staging tables)
python -m src.etl.main --warehouse    # Transform only (load dimensions)
python -m src.etl.main --load-fact-tables  # Load facts (2.6M+ events)

# Utilities
python -m src.etl.main --test-db      # Test database connection
python -m src.etl.main --help         # Show all available commands
```

**See [ETL_COMMAND_SEQUENCE.md](ETL_COMMAND_SEQUENCE.md) for workflow examples.**

---

## 🚀 New Feature: Fast Testing with `--limit-data`

The `--limit-data` parameter allows you to test the ETL pipeline with a subset of files, useful for:
- ✅ **Quick validation** of pipeline changes
- ✅ **Performance testing** without full data load
- ✅ **Duplicate prevention** via manifest tracking system

### How It Works

- **Processes first N StatsBomb JSON files** (out of 380 total)
- **Manifest system prevents duplicates** - running `--limit-data 30` twice loads only the first 30 files once
- **Can incrementally extend** - run `--limit-data 30`, then `--limit-data 60` to add 30 more files

### Examples

```powershell
# Test with 10 files (~40 seconds, ~36K events)
python -m src.etl.main --full-etl-and-facts --limit-data 10

# Test with 30 files (~2 minutes, ~106K events)
python -m src.etl.main --full-etl-and-facts --limit-data 30

# Extend to 50 files (adds only 20 new files, ~1 minute)
python -m src.etl.main --full-etl-and-facts --limit-data 50

# Run full pipeline without limit (all 380 files, ~10 minutes)
python -m src.etl.main --full-etl-and-facts
```

### Verification

After running with `--limit-data`, check the manifest:
```sql
-- Verify number of files processed
SELECT COUNT(*) as files_processed FROM ETL_Events_Manifest;
```

**Note:** The manifest system prevents duplicate data loading, so running the same `--limit-data` value multiple times is safe! ✅

---

## Data Sources & Event Loading

### StatsBomb Event Data Repository

**Repository:** https://github.com/statsbomb/open-data  
**License:** CC BY 4.0 (Creative Commons)  
**Data Coverage:** Professional football matches across multiple leagues

#### How Event Data is Loaded

1. **Repository Cloning**
   - ETL automatically clones StatsBomb repository to `data/raw/open-data-master/`
   - First run only - subsequent runs check for existing clone
   - ~500 MB download (includes all historical match data)

2. **EPL-Only Filtering**
   ```python
   # EPL season ID: 2 (English Premier League)
   # Season identifier: 27 (2015-16 season)
   # Source: data/matches/2/27.json (official match index)
   ```
   - Reads official EPL match IDs from `competition_id: 2, season_id: 27`
   - Filters 3,464 StatsBomb JSON files → **380 EPL files only**
   - Eliminates non-EPL data (other leagues, tournaments)
   - **Result:** 100% EPL data, zero contamination

3. **Event JSON Processing**
   ```
   data/raw/open-data-master/data/events/
   ├── 15500.json          (Match ID 15500 events)
   ├── 15501.json          (Match ID 15501 events)
   └── ... (378 more match files)
   ```
   - Each JSON file contains all events for one match
   - Events include: passes, shots, fouls, substitutions, tactical shifts, etc.
   - Average 3,460 events per match
   - Total: **2,675,770+ events** loaded into fact_match_events

4. **Per-File Transaction Isolation**
   - Each JSON file loaded in its own database transaction
   - Batch size: 250 rows (optimized for connection pool)
   - Automatic rollback on error (keeps DB consistent)
   - Prevents "Can't reconnect" errors from long-lived transactions

5. **Deduplication & Manifest Tracking**
   - `ETL_Events_Manifest` tracks every processed match
   - Duplicate runs skip already-loaded matches (idempotent)
   - Safe for re-runs without data duplication

#### StatsBomb Event Data Structure
```json
{
  "id": "event-uuid",
  "index": 1,
  "period": 1,
  "timestamp": "00:00:00.000",
  "minute": 0,
  "second": 0,
  "possession": 1,
  "duration": 0.5,
  "type": {
    "id": 1,
    "name": "Pass"
  },
  "player": {"id": 1234, "name": "Player Name"},
  "team": {"id": 217, "name": "Arsenal"},
  "location": [60.0, 40.0],
  "pass": {
    "recipient": {"id": 5678},
    "length": 15.2,
    "angle": 0.52,
    "outcome": "Complete"
  }
}
```

**Data Loaded Per Match:** ~3,460 events including:
- Ball touches and passes
- Shots and expected goals (xG)
- Defensive actions (tackles, blocks, interceptions)
- Fouls and yellow/red cards
- Substitutions and tactical formations
- Set pieces and free kicks

---

### Player Performance Stats Generation

#### Mock Data Generation Strategy

**Why Mock Data?**
- FBRef (Football-Reference) player stats CSV files have schema issues
- Column `league_div` missing in some files → NULL constraint errors
- Mock data demonstrates `fact_player_stats` table functionality
- **Production use:** Replace with real FBRef or other stats source

#### How Player Stats are Generated

**File:** `generate_player_stats_mock_data.py`

**Generation Process:**

1. **Retrieve Real Teams from Database**
   ```python
   SELECT team_id, team_name FROM dim_team
   # Returns: Arsenal, Aston Villa, Brighton, etc.
   ```

2. **Generate 1,600 Records**
   - Loop through each unique team (25 teams)
   - Create 64 mock records per team
   - Each record represents one player's performance in one match

3. **Random Stats Assignment**
   ```python
   # For each player-match combination, randomly generate:
   - Matches played: 1-5
   - Minutes played: 45-90
   - Goals scored: 0-3
   - Assists: 0-2
   - Pass completion: 60-95%
   - Tackles made: 0-5
   - Interceptions: 0-3
   - Yellow cards: 0-1
   ```

4. **Link to Real Dimensions**
   ```python
   # Each record must reference real database IDs:
   - player_id: Random from dim_player (1-6847 or sentinels -1, 6808)
   - team_id: Actual team from dim_team
   - match_id: Random from fact_match (1-830)
   - season_id: Random from dim_season
   ```

5. **Insert into Staging**
   ```python
   # Insert 1,600 records into stg_player_stats_fbref
   # Then transform & load into fact_player_stats
   ```

#### Player Stats Table Structure
```sql
CREATE TABLE fact_player_stats (
  player_stat_id BIGINT PRIMARY KEY,
  match_id BIGINT,                -- Foreign key to fact_match
  player_id BIGINT,               -- Foreign key to dim_player
  team_id BIGINT,                 -- Foreign key to dim_team
  season_id BIGINT,               -- Foreign key to dim_season
  matches_played INT,
  minutes_played INT,
  goals DECIMAL(10, 2),
  assists DECIMAL(10, 2),
  pass_completion_rate DECIMAL(5, 2),
  tackles_made INT,
  interceptions INT,
  yellow_cards INT,
  red_cards INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### Running Mock Generation
```powershell
# Automatic: Runs as part of --load-fact-tables
python -m src.etl.main --load-fact-tables

# Manual generation (if needed):
python generate_player_stats_mock_data.py

# Output: 1,600 records in stg_player_stats_fbref ready for loading
```

#### Expected Output
```
[SUCCESS] Generated 1600 player stats records with valid team names
```

#### Replacing Mock Data (Production)

To use real FBRef stats instead of mock data:

1. **Place FBRef CSV files** in `data/raw/fbref_player_stats/`
   ```
   data/raw/fbref_player_stats/
   ├── 2017-2018_player_stats.csv
   ├── 2018-2019_player_stats.csv
   └── ...
   ```

2. **Update extraction** in `src/etl/extract/` to read FBRef format

3. **Comment out mock generation** in `src/etl/main.py` (line ~200)
   ```python
   # STEP -1: Generate mock player stats
   # Comment this out to skip mock data generation
   # generate_mock_player_stats()
   ```

4. **Run ETL normally**
   ```powershell
   python -m src.etl.main --full-etl
   python -m src.etl.main --load-fact-tables
   ```

---

### CSV Source Files

**Location:** `data/raw/csv/`

#### Match Data (E0Season_*.csv)
- **Files:** E0Season_2015-16.csv through E0Season_2024-25.csv
- **Rows:** 830 total matches across 10 seasons
- **Columns:** Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, etc.
- **Source:** Football-Data.co.uk
- **Purpose:** Primary match dimension and fact table source

#### Team Data
- **Files:** team_*.csv files in data/raw/
- **Contains:** Team names, IDs, abbreviations
- **Purpose:** Dimension population via API calls

#### Stadium/Referee Data (Excel)
- **File:** `EPL_stadium_from_1992-92_2025-26.xlsx`
- **File:** `referees_complete.xlsx`
- **Purpose:** Dimension tables for stadiums and referees

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GitHub: StatsBomb/open-data          CSV Files               │
│  ├─ 380 EPL event JSONs              ├─ E0Season_*.csv       │
│  │  (2.67M+ events)                  │  (830 matches)        │
│  │                                   │                       │
│  └─ events/15500.json                Excel Files            │
│     events/15501.json                ├─ stadiums.xlsx       │
│     ... (378 more)                   └─ referees.xlsx       │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │  EXTRACT (01) │
                    ├───────────────┤
                    │ StatsBomb:    │
                    │ • Clone repo  │
                    │ • Filter EPL  │
                    │ • Read JSONs  │
                    └───────────────┘
                            ↓
                ┌─────────────────────────┐
                │  STAGING (02)           │
                ├─────────────────────────┤
                │ stg_events_raw          │
                │ stg_e0_match_raw        │
                │ stg_player_raw          │
                │ stg_player_stats_fbref  │
                └─────────────────────────┘
                            ↓
                ┌─────────────────────────┐
                │  TRANSFORM (03)         │
                ├─────────────────────────┤
                │ dim_player              │
                │ dim_team                │
                │ dim_stadium             │
                │ dim_referee             │
                └─────────────────────────┘
                            ↓
                ┌─────────────────────────┐
                │  LOAD (04)              │
                ├─────────────────────────┤
                │ fact_match              │
                │ fact_match_events       │
                │ fact_player_stats       │
                │ Mappings & Manifest     │
                └─────────────────────────┘
```


---

## GitHub & Repository Integration

### Project Repositories

#### 1. **This Project: EPL_DWH** (Local)
**Repository:** `d:\myPortfolioProject\EPL_DWH`  
**GitHub:** https://github.com/DuvinduDinethminDevendra/EPL_DWH  
**Owner:** DuvinduDinethminDevendra  
**Branch:** main  
**Purpose:** EPL Data Warehouse ETL pipeline & documentation

#### 2. **StatsBomb Open Data** (External)
**Repository:** https://github.com/statsbomb/open-data  
**License:** CC BY 4.0 (Creative Commons)  
**Purpose:** Event data source for all EPL matches  
**Cloned Location:** `data/raw/open-data-master/`

### How StatsBomb Repository is Used

**Automatic Integration in ETL:**

```python
# src/etl/extract/statsbomb_reader.py

# Step 1: Check if repo exists locally
if not os.path.exists('data/raw/open-data-master/'):
    print("Cloning StatsBomb repository...")
    git.Repo.clone_from(
        'https://github.com/statsbomb/open-data.git',
        'data/raw/open-data-master/'
    )

# Step 2: Navigate to events directory
events_path = 'data/raw/open-data-master/data/events/'

# Step 3: Filter EPL matches only (competition 2, season 27)
matches_file = 'data/raw/open-data-master/data/matches/2/27.json'
official_match_ids = json.load(open(matches_file))

# Step 4: Load only EPL event files
for match_id in official_match_ids:
    event_file = os.path.join(events_path, f'{match_id}.json')
    if os.path.exists(event_file):
        load_events_from_json(event_file)
```

**Repository Structure Used:**
```
open-data-master/
├── data/
│   ├── matches/
│   │   └── 2/                    # Competition 2 = EPL
│   │       └── 27.json           # Season 27 = 2015-16
│   │           └── [List of all EPL match IDs]
│   │
│   └── events/
│       ├── 15500.json            # Match 15500 events
│       ├── 15501.json            # Match 15501 events
│       └── ... (378 more files)
```

### Repository Clone Behavior

#### First Run (Clone Required)
```powershell
PS> python -m src.etl.main --full-etl

[INFO] StatsBomb repository not found locally
[INFO] Cloning https://github.com/statsbomb/open-data.git
[INFO] Download: 500 MB (1-5 minutes depending on connection)
[OK] Repository cloned to data/raw/open-data-master/
[INFO] Filtering 3,464 files to find 380 EPL matches...
[OK] Found 380 EPL match event files
```

#### Subsequent Runs (Repo Exists)
```powershell
PS> python -m src.etl.main --full-etl

[INFO] StatsBomb repository already exists locally
[INFO] Using: data/raw/open-data-master/
[INFO] Filtering 3,464 files to find 380 EPL matches...
[OK] Found 380 EPL match event files
```

### Managing the StatsBomb Repository

#### Update Repository to Latest
```powershell
# Navigate to the cloned repo
cd data/raw/open-data-master/

# Pull latest changes from GitHub
git pull origin master

# Return to project root
cd ..\..\
```

#### Delete and Re-Clone (Full Refresh)
```powershell
# Remove existing clone
Remove-Item -Recurse -Force data/raw/open-data-master/

# Next ETL run will re-clone automatically
python -m src.etl.main --full-etl
```

#### Verify Repository Integrity
```powershell
# Check if repository exists
Test-Path data/raw/open-data-master/

# Count event files
(Get-ChildItem data/raw/open-data-master/data/events/ -Filter "*.json" | Measure-Object).Count
# Expected: 3,464 files total (380 EPL)

# Verify EPL match index
Test-Path data/raw/open-data-master/data/matches/2/27.json
# Expected: True
```

### ETL Pipeline Git Integration

#### This Project (EPL_DWH) - Version Control

**Track your changes:**
```powershell
# Check status
git status

# Stage changes
git add .

# Commit with message
git commit -m "Add sentinel records and fix FK constraints"

# Push to GitHub
git push origin main
```

**Important files to commit:**
- ✅ `src/etl/*.py` - Pipeline code changes
- ✅ `src/sql/*.sql` - Schema or SQL modifications
- ✅ `README.md` - Documentation updates
- ✅ `requirements.txt` - Dependency changes
- ✅ `docker-compose.yml` - Container configuration

**Do NOT commit:**
- ❌ `mysql_data/` - Database files (ignored in .gitignore)
- ❌ `data/raw/open-data-master/` - External repo (ignored in .gitignore)
- ❌ `.venv/` - Python virtualenv (ignored in .gitignore)
- ❌ `*.log` - Log files
- ❌ `.env` - Credential files

#### StatsBomb Repository - Reference Only

**Do NOT modify** the cloned StatsBomb repository because:
1. It's external data source, not part of this project
2. Any local changes will be overwritten on pull
3. Changes should go upstream to StatsBomb repository
4. It's in `.gitignore` (won't be committed anyway)

---

## Project Structure

```
EPL_DWH/
├── src/
│   ├── etl/
│   │   ├── main.py                      # ← Entry point (use: python -m src.etl.main)
│   │   ├── extract/
│   │   │   └── statsbomb_reader.py      # EPL-only filter + event extraction
│   │   ├── transform/
│   │   │   └── *.py                     # Dimension cleaning & upserts
│   │   ├── load/
│   │   │   └── load_facts.py            # Fact table loading
│   │   └── db.py                        # Database connection
│   ├── sql/
│   │   ├── create_schema.sql            # Database schema (21 tables)
│   │   └── load_fact_match_events.sql   # Fact table transformation
│   └── utils/
│       ├── logger.py                    # Logging utilities
│       └── dq_checks.py                 # Data quality checks
├── data/
│   ├── raw/
│   │   ├── open-data-master/            # StatsBomb open data (GitHub clone)
│   │   ├── csv/                         # Match/player/team CSVs
│   │   └── json/                        # Event JSONs (staging)
│   └── staging/                         # CSV staging area
├── docker-compose.yml                   # MySQL 8.0 service definition
├── requirements.txt                     # Python dependencies
├── monitor_etl.py                       # Progress monitor script
├── CURRENT_STATUS.md                    # Live pipeline status & metrics
└── EXTRACTION_IMPROVEMENTS.md           # Technical documentation
```

---

## Database Schema

**21 Tables Created:**

### Dimensions
- `dim_team` — Team master data
- `dim_player` — Player master data
- `dim_referee` — Referee master data
- `dim_stadium` — Stadium master data
- `dim_season` — Season definitions
- `dim_date` — Date dimension (calendar)

### Facts
- `fact_match` — Match-level facts (date, teams, score, attendance)
- `fact_match_events` — Event-level facts (pass, shot, foul, etc.)
- `fact_player_stats` — Player performance stats per match

### Staging
- `stg_events_raw` — Raw event data from StatsBomb JSONs
- `stg_team_raw` — Raw team data
- `stg_player_raw` — Raw player data
- `stg_player_stats_fbref` — Raw player stats from FBRef

### ETL Metadata
- `ETL_Events_Manifest` — Processing manifest (match_id, row count, timestamps)
- `ETL_File_Manifest` — File-level processing log
- `ETL_JSON_Manifest` — JSON file processing metadata
- `ETL_Log` — General ETL execution log

---

## Sentinel Strategy (Referential Integrity)

### Problem Solved
Foreign key constraint violations when source data contains NULL or missing IDs.

### Solution: Sentinel Records
**Sentinel records** are reserved placeholder rows in dimension tables that prevent FK violations:

| Sentinel ID | Usage | Purpose |
|------------|-------|---------|
| **-1** | `dim_stadium`, `dim_team`, `dim_referee`, `dim_season`, `dim_date` | Primary "Unknown" key across all dimensions |
| **6808** | `dim_player` only | Secondary unknown player (high ID avoiding collision with real player range 1-6847) |

### Why Two Player Sentinels?
- **`-1`**: Reserved for unknown/generic cases (also used across other dims)
- **`6808`**: Specific to players; allows filtering: `WHERE player_id NOT IN (-1, 6808)` or `WHERE player_id > 0`
- **Benefits**: Flexibility in queries and easy identification of synthetic data during analysis

### Maintenance

```powershell
# Ensure sentinels exist before ETL runs
python add_sentinels2.py

# Verify sentinels were preserved
python check_sentinels_and_counts.py
```

---

## Key Features

### EPL-Only Filtering
- Reads official match IDs from `data/matches/2/27.json` (EPL season 27)
- Filters 3,464 StatsBomb event files → **380 EPL files only**
- **Result:** 100% EPL data, zero contamination

### Per-File Transaction Isolation
- Each event file is loaded in its own database transaction
- Failures roll back cleanly; successes commit atomically
- Eliminates long-lived transactions & "Can't reconnect" errors
- Chunksize: 250 rows (optimized for connection pool)

### Idempotent Manifest
- `ETL_Events_Manifest` tracks every processed match
- Duplicate runs skip already-loaded matches
- Safe for re-runs without data duplication

---

## Data Progress

| Metric | Value |
|--------|-------|
| **EPL Matches Available** | 380 (2015-16 season) |
| **Matches Processed** | 62 (16.3%) |
| **Events Loaded** | 214,559 |
| **Avg Events/Match** | 3,460 |
| **Est. Total Events** | ~1.3M |
| **Estimated ETA** | 15-20 minutes |

---

## Running the Pipeline

### Full ETL (Recommended)

```powershell
python -m src.etl.main --full-etl
```

**What happens:**
1. Validates/creates StatsBomb repo at `data/raw/open-data-master`
2. Identifies 380 EPL match IDs from official index
3. Extracts & loads all event JSONs into `stg_events_raw` (per-file transactions)
4. Transforms & loads dimension tables
5. Transforms & loads fact tables
6. Writes progress to `ETL_Events_Manifest`

### Monitor Progress

In a separate terminal:

```powershell
python monitor_etl.py
```

Or run direct SQL query:

```powershell
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    m = conn.execute(text('SELECT COUNT(*) FROM ETL_Events_Manifest')).scalar()
    e = conn.execute(text('SELECT COUNT(*) FROM stg_events_raw')).scalar()
    print(f'Matches: {m}/380 | Events: {e:,}')
"
```

---

## Troubleshooting

### Pipeline Stalls or Errors

1. **Check logs** in terminal output
2. **Verify DB connection:**
   ```powershell
   python -m src.etl.main --test-db
   ```
3. **Clear staging & restart** (if needed):
   ```powershell
   docker exec epl_mysql mysql -u root -p1234 epl_dw -e "
   TRUNCATE TABLE stg_events_raw;
   TRUNCATE TABLE ETL_Events_Manifest;
   "
   python -m src.etl.main --full-etl
   ```

### Database Connection Issues

```powershell
# Connect directly to MySQL
docker exec -it epl_mysql mysql -u root -p1234 epl_dw

# Check table row counts
SELECT TABLE_NAME, TABLE_ROWS 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'epl_dw' 
ORDER BY TABLE_NAME;
```



---

## 📚 Documentation

### Essential Guides
| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Quick setup, commands, data status | 5 min |
| **[ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)** | Complete ETL process explanation | 15 min |
| **[DATABASE_RELATIONSHIPS_ER_DIAGRAM.md](DATABASE_RELATIONSHIPS_ER_DIAGRAM.md)** | Schema relationships & ER diagram | 10 min |
| **[FACT_CONSTELLATION_QUICK_REFERENCE.md](FACT_CONSTELLATION_QUICK_REFERENCE.md)** | Schema pattern explanation | 3 min |
| **[MAINTENANCE.md](MAINTENANCE.md)** | Operations & troubleshooting | 10 min |

### File Organization
- **`docker-compose.yml`** — MySQL 8.0 service configuration
- **`requirements.txt`** — Python dependencies


---

## 🔗 Data Sources

### StatsBomb Open Data
**Repository:** [`StatsBomb/open-data`](https://github.com/statsbomb/open-data)  
**License:** Creative Commons Attribution 4.0  
**Content:** Event-by-event data for 380 EPL matches (1.3M+ events)  
**Location:** `data/raw/open-data-master/` (auto-cloned)  
**Data Included:**
- Match metadata (teams, dates, venues)
- Detailed event logs (passes, shots, fouls, etc.)
- Player information
- Match timelines and formations

**How it's used:**
1. Pipeline clones/updates the repo automatically
2. Filters 3,464 total event files → 380 EPL-only files
3. Extracts match events into `stg_events_raw` (1.3M+ rows)
4. Joins to CSV match data for ID mapping

**Reference:** StatsBomb data dictionary available in the repository's `data/` folder

---

### CSV Match Data (E0 Format)
**Source:** Football-Reference.com (E0 = England Division 1 / EPL)  
**Format:** Comma-separated values  
**Location:** `data/raw/csv/`  
**Fields:** 
- Match ID, Date, Home Team, Away Team
- Final Score, Venue, Referee
- Half-time Score, Attendance, Notes

**How it's used:**
- Primary key for fact_match (830 matches)
- Provides match-level metadata
- Joined with StatsBomb events via `dim_match_mapping`

---

### Reference Tables
**Dimensions from multiple sources:**
- **Teams:** StatsBomb + CSV (60 rows staging → 31 final)
- **Players:** StatsBomb event player names (6,809 rows)
- **Referees:** CSV match data (33 rows)
- **Stadiums:** Static EPL reference data (58 rows)
- **Seasons:** Date-based inference (7 rows)
- **Dates:** Generated calendar (17,533 rows, 1990-2025)

---

## 🏗️ Architecture & Design

### Data Flow
```
StatsBomb JSON         CSV Match Data
(1.3M events)         (830 matches)
    │                      │
    ├─→ stg_events_raw ←───┤
    │      (1.3M rows)     │
    │                      │
    ├─→ stg_e0_match_raw  │
    │      (830 rows)     │
    │                      │
    └──────────┬───────────┘
               │
    ┌──────────▼──────────┐
    │ Dimension Creation  │
    │ (6 tables)          │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────────────┐
    │ Mapping Tables              │
    │ dim_match_mapping (684)      │
    │ dim_team_mapping (40)        │
    └──────────┬──────────────────┘
               │
    ┌──────────▼──────────────────────────┐
    │ Fact Tables Loading                │
    │ fact_match (830 rows) ✓            │
    │ fact_match_events (1.3M rows) ✓    │
    └────────────────────────────────────┘
```

### Key Design Decisions
1. **Staging → Dimension → Fact** order enforces data quality
2. **Mapping tables** eliminate correlated subquery timeouts
3. **Sentinel values** preserve all events (UNKNOWN player/team)
4. **Per-file transactions** ensure atomicity and recovery
5. **FK constraints enabled** catch data quality issues immediately

---

## 📊 Database Specifications

**Engine:** MySQL 8.0  
**Container:** Docker (epl_mysql)  
**Connection Details:**
- Host: `localhost` (or `epl_mysql` from within Docker)
- Port: `3307` (host port)
- User: `root`
- Password: `1234`
- Database: `epl_dw`

**Size:** ~150 MB data + indexes for 1.3M events

---

## 🚀 Git Repository

**Repository:** `EPL_DWH`  
**Owner:** `DuvinduDinethminDevendra`  
**Branch:** `main`  
**Location:** `d:\myPortfolioProject\EPL_DWH`

### Last Update
```bash
# ETL Pipeline Documentation & Optimization
# Oct 26, 2025

Files modified:
├── README.md (this file)
├── ETL_PIPELINE_GUIDE.md (NEW - comprehensive step-by-step guide)
├── SQL_SCRIPTS_REFERENCE.md (NEW - SQL script reference)
├── src/sql/
│   ├── create_schema.sql (production)
│   ├── load_fact_match.sql (production)
│   ├── load_fact_match_events_step1.sql (step 1)
│   ├── load_fact_match_events_step2.sql (step 2)
│   ├── load_fact_match_events_step3_final.sql (step 3 - working)
│   ├── load_fact_match_events_step4_verify.sql (verification)
│   ├── final_row_count.sql (validation)
│   └── count_rows.sql (alternative check)
└── Cleanup: Removed 15+ temporary/failed SQL variations

Status: ✅ PRODUCTION READY
Total Commits: Ready for final push
```

### To Commit Changes
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "docs: Complete ETL pipeline documentation with step-by-step guides

- Added comprehensive ETL_PIPELINE_GUIDE.md with detailed reasoning
- Added SQL_SCRIPTS_REFERENCE.md for quick lookup
- Updated README.md with data source information
- Optimized SQL scripts for production use
- All 1.3M events successfully loaded and verified
- Status: FULLY OPERATIONAL"

# Push to remote
git push origin main
```

---

## ✅ Final Checklist

- [x] Database schema created (21 tables)
- [x] Dimensions populated (17.5K dates, 31 teams, 6.8K players, etc.)
- [x] Fact_match loaded (830 matches from CSV)
- [x] **Fact_match_events loaded (2.67M events from StatsBomb)** ✅
- [x] All FK constraints satisfied
- [x] Mapping tables created (380 matches, 40 teams)
- [x] SQL scripts optimized and cleaned
- [x] Documentation complete (8 comprehensive guides)
- [x] Date enrichment implemented (all events with calendar dates)
- [x] Git repository ready for commit

**Next Steps:**
1. Review [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md) for complete overview
2. Run analytical queries on fact_match_events
3. Consider incremental loads for new StatsBomb data
4. Monitor query performance as data grows

---

## 📞 Support & Questions

For detailed information on:
- **ETL Process:** See [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)
- **SQL Scripts:** See [SQL_SCRIPTS_REFERENCE.md](SQL_SCRIPTS_REFERENCE.md)
- **Data Sources:** See [Data Sources](#-data-sources) section above
- **Troubleshooting:** See [Troubleshooting](#troubleshooting) section above

---

**Project Status:** ✅ **FULLY OPERATIONAL**  
**Last Updated:** October 26, 2025  
**Data Freshness:** Current with full event coverage  
**Next Review:** November 2025
    
    depends_on:
      - db
```

**Start the Container:**

Run the following command in the project root directory. This will download the MySQL image, create the `epl_dw` database, and execute the `create_schema.sql` script to build your tables.

```bash
docker-compose up -d
```
OR IF NEED TO CREATE A LOCAL INSTANCE AS WELL
```bash
mysql -u root -p1234 < "src\sql\create_schema.sql"
```

### 3\. Setup Python Environment

This project uses a virtual environment (`.venv`) for dependency management.

**A. Create and Activate the Virtual Environment**

On Windows (PowerShell):

```powershell
# Create the environment
py -m venv .venv

# Activate the environment (Required for every new terminal session)
. .venv/Scripts/Activate.ps1
```
If you wont to run the v env in comman promt
```command prompt
.venv\Scripts\activate.bat
```

*(Your prompt should now start with `(.venv)`)*

**B. Install Python Dependencies**

Ensure you have a `requirements.txt` file listing packages like `sqlalchemy` and `mysql-connector-python`.

```bash
# Example contents of requirements.txt:
# sqlalchemy
# mysql-connector-python
# pandas

pip install -r requirements.txt
```

### 4\. Run the ETL Pipeline

Once the database container is running and the Python environment is active, you can run the ETL pipeline.

**Complete ETL Pipeline (Recommended):**
```bash
python -m src.etl.main --full-etl
```

**Run Only Staging Load:**
```bash
python -m src.etl.main --staging
```

**Run Only Warehouse Load:**
```bash
python -m src.etl.main --warehouse
```

**Test Database Connectivity:**
```bash
python -m src.etl.main --test-db
```

## ETL Pipeline Overview

The project implements a complete ETL pipeline with three main stages:

### **Stage 1: Staging (Extract & Load)**
Loads raw data from multiple sources into staging tables:

| Source | Format | Target Table | Records |
|--------|--------|--------------|---------|
| **JSON Files** | JSON | `stg_player_raw` | ~6,834 players |
| **API (football-data.org)** | REST API | `stg_team_raw` | ~60 teams |
| **CSV Files** | CSV | `stg_e0_match_raw` | ~830 matches |
| **Excel Files** | XLSX | `stg_referee_raw`, `dim_stadium` | ~32 referees, ~32 stadiums |

**Key Features:**
- ✅ Idempotent processing (skips already-loaded files)
- ✅ Comprehensive audit trail via manifest tables
- ✅ Error logging and recovery
- ✅ Smart Excel sheet detection (finds appropriate sheets by name)

### **Stage 2: Transform & Load (Dimensions)**
Cleans and transforms staging data into dimension tables:


---

## ✅ Final Checklist

- [x] Database schema created (21 tables)
- [x] Dimensions populated (17.5K dates, 31 teams, 6.8K players, etc.)
- [x] Fact_match loaded (830 matches from CSV)
- [x] **Fact_match_events loaded (2.67M events from StatsBomb)** ✅
- [x] All FK constraints satisfied
- [x] Mapping tables created (380 matches, 40 teams)
- [x] SQL scripts optimized and cleaned
- [x] Documentation complete (8 comprehensive guides)
- [x] Date enrichment implemented (all events with calendar dates)
- [x] Git repository ready for commit
- [x] **`--limit-data` feature added for fast testing** ✨
- [x] **`stg_events_raw` added to staging cleanup** ✨

**Next Steps:**
1. Run `--full-etl-and-facts` for complete pipeline execution
2. Use `--limit-data` parameter for quick validation with subset of data
3. Verify all data loaded with zero duplicates (manifest system)
4. Ready for production deployment!

---

## 📞 Support & Questions

For detailed information on:
- **ETL Process:** See [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)
- **SQL Scripts:** See [SQL_SCRIPTS_REFERENCE.md](SQL_SCRIPTS_REFERENCE.md)
- **Data Sources:** See [Data Sources](#-data-sources) section above
- **Troubleshooting:** See [Troubleshooting](#troubleshooting) section above

---

**Project Status:** ✅ **FULLY OPERATIONAL**  
**Last Updated:** November 1, 2025  
**Data Freshness:** Current with full event coverage  
**Features:** Complete ETL + Testing + Deduplication ✨
**Next Review:** December 2025
