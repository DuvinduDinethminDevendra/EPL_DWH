# EPL Data Warehouse

An ETL pipeline that ingests **StatsBomb open-data event files** for English Premier League matches and builds a **Star Schema data warehouse** in MySQL.

**Status:** ✅ **FULLY OPERATIONAL**
- **1,362,577 match events** loaded and verified
- **342 matches** with complete event coverage
- **All FK constraints satisfied**
- **Execution time:** ~11 minutes

📖 **[Read the Complete ETL Pipeline Guide](ETL_PIPELINE_GUIDE.md)** ← Detailed steps, reasoning, and data flows

---

## Current Data State

### ✅ All Data Successfully Loaded

| Category | Table | Rows | Status |
|----------|-------|------|--------|
| **Dimensions** | dim_date | 17,533 | ✓ |
| | dim_team | 31 | ✓ |
| | dim_season | 7 | ✓ |
| | dim_player | 6,809 | ✓ |
| | dim_referee | 33 | ✓ |
| | dim_stadium | 58 | ✓ |
| **Facts** | fact_match | 830 | ✓ All CSV matches |
| | **fact_match_events** | **1,362,577** | ✓ **All StatsBomb events** |
| | fact_player_stats | 0 | (Optional) |
| **Staging** | stg_events_raw | 1,313,783 | ✓ |
| | stg_e0_match_raw | 830 | ✓ |
| **Mappings** | dim_match_mapping | 684 | ✓ CSV↔StatsBomb pairs |
| | dim_team_mapping | 40 | ✓ Team ID translation |

### Key Metrics

- **Total Events:** 1,362,577 match events from StatsBomb
- **Matches Covered:** 342 matches with complete event data
- **Players:** 286 unique + 1 UNKNOWN (for unmapped player names)
- **Teams:** 20 EPL teams + 1 UNKNOWN
- **Load Time:** ~11 minutes (efficient, no timeouts)
- **Data Quality:** All FK constraints satisfied; zero referential integrity violations

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

### 3. Activate Python Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. The ETL Pipeline is Ready to Use

All data has been successfully loaded! The pipeline includes:
- ✓ StatsBomb event extraction (1.3M+ events)
- ✓ CSV match data loading (830 matches)
- ✓ Dimension population (teams, players, referees, dates, stadiums, seasons)
- ✓ Fact table loading (matches and events with full referential integrity)
- ✓ Mapping tables for ID translation (684 match pairs, 40 team mappings)

### Usage Examples

```powershell
# Complete ETL: Staging + Dimensions + Fact Tables (recommended)
python -m src.etl.main --full-etl          # Step 1: Extract & load dimensions
python -m src.etl.main --load-fact-tables  # Step 2: Load all fact tables

# Or run individual steps
python -m src.etl.main --staging      # Load raw data to staging only
python -m src.etl.main --warehouse    # Load dimensions from staging
python -m src.etl.main --load-fact-tables  # Load fact tables (1.3M events)

# Utility commands
python -m src.etl.main --test-db      # Test database connection
```

**📖 See [LOAD_FACT_TABLES_GUIDE.md](LOAD_FACT_TABLES_GUIDE.md) for detailed instructions on the `--load-fact-tables` command.**

---

## Alternative Commands

```powershell
# Test database connection only
python -m src.etl.main --test-db

# Load staging data only (extract)
python -m src.etl.main --staging

# Load dimensions only (transform - requires staging first)
python -m src.etl.main --warehouse

# ✅ NEW: Load fact tables (run after --full-etl)
# Executes all 6 SQL scripts in sequence: 830 matches + 1.36M events
python -m src.etl.main --load-fact-tables
```

**See [LOAD_FACT_TABLES_GUIDE.md](LOAD_FACT_TABLES_GUIDE.md) for details on each command and workflow examples.**

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

---

## 📚 Documentation

### Primary Guides
- **[ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)** ⭐ **START HERE** 
  - Complete step-by-step ETL process explanation
  - Why each step is necessary
  - Data transformations and flows
  - Performance notes and design decisions

- **[SQL_SCRIPTS_REFERENCE.md](SQL_SCRIPTS_REFERENCE.md)** 
  - Quick reference for all SQL scripts
  - Execution instructions
  - Troubleshooting guide
  - Performance benchmarks

### Additional Resources
- **`CURRENT_STATUS.md`** — Live pipeline status, progress metrics
- **`EXTRACTION_IMPROVEMENTS.md`** — Technical details on EPL filtering
- **`docker-compose.yml`** — MySQL service configuration
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
- [x] **Fact_match_events loaded (1.36M events from StatsBomb)** ✅
- [x] All FK constraints satisfied
- [x] Mapping tables created (684 matches, 40 teams)
- [x] SQL scripts optimized and cleaned
- [x] Documentation complete (3 comprehensive guides)
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

| Dimension | Records | Key Attributes |
|-----------|---------|-----------------|
| `dim_date` | 17,803 | Calendar 1992-2040 with week numbers |
| `dim_team` | 25 | Team name, code, city |
| `dim_player` | 6,834 | Player name, position, nationality |
| `dim_referee` | 32 | Name, DOB, nationality, PL debut, status |
| `dim_stadium` | 32 | Name, capacity, city, club, coordinates |
| `dim_season` | 6 | Season name, start/end dates |

**Cleaning Logic:**
- Standardizes team names (handles "Man City" → "Manchester City" mappings)
- Removes duplicates and null values
- Creates surrogate keys and business keys

### **Stage 3: Load (Facts)**
Loads fact tables with foreign key references to dimensions:

| Fact Table | Records | Measures |
|-----------|---------|----------|
| `fact_match` | 830 | Goals, shots, fouls, cards, results |
| `fact_match_events` | - | Event type, player, minute (ready) |
| `fact_player_stats` | - | Minutes, goals, assists, cards (ready) |

## Data Sources

### Excel Files
Place Excel files in `data/raw/xlsx/` folder. The system automatically detects:
- **Referee files** (containing "referee" in filename) → loads to `stg_referee_raw`
- **Stadium files** (containing "stadium" in filename) → loads to `dim_stadium`

**Expected Column Names:**
- **Referees:** `Referee_Name`, `Date_of_Birth`, `Nationality`, `Premier_League_Debut`, `Status`, `Notes`
- **Stadiums:** `Stadium_Name`, `Capacity`, `City`, `Club`, `Opened`, `Coordinates`, `Notes`

### API Integration
- **football-data.org API** - Fetches current team data for seasons 2023-2025
- Stores full API responses including squads and staff details

### CSV Files
- **E0 Series (fbref)** - Match results from football-reference.com
- Supports multiple seasons and divisions

### JSON Files
- **Squad data** - Player information from football-data.org
- Nested player and staff information

## Data Warehouse Schema

### Key Design Patterns

**1. Date Dimension (Type 1 - Slowly Changing)**
- Pre-populated calendar from 1992 to 2040
- Supports week-based analysis
- Extensible for match day flags

**2. Team Conformation**
- Uses CASE statement CTE to map raw team names to canonical forms
- Handles abbreviations and historical naming variations

**3. Surrogate Keys**
- Sentinel rows (-1) for unknown/missing dimensions
- Ensures referential integrity with NOT NULL constraints

**4. Audit Trail**
- `ETL_Log` - Records all ETL job execution details
- `ETL_File_Manifest` - Tracks CSV file loads
- `ETL_Api_Manifest` - Tracks API calls
- `ETL_Excel_Manifest` - Tracks Excel file loads
- `ETL_JSON_Manifest` - Tracks JSON file loads

## Architecture

```
┌─────────────────────────────────────────────────┐
│         DATA EXTRACTION LAYER                   │
├─────────────────────────────────────────────────┤
│ JSON Reader │ API Client │ CSV Reader │ Excel   │
│             │            │           │ Reader  │
└──────────────┬───────────┬───────────┬──────────┘
               │           │           │
┌──────────────▼───────────▼───────────▼──────────┐
│        STAGING TABLES (Raw Data)                │
├──────────────────────────────────────────────────┤
│ stg_player_raw │ stg_team_raw │ stg_e0_match... │
│ stg_referee_raw │ stg_player_stats_fbref      │
└─────────────┬──────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────┐
│        TRANSFORM & CLEAN LAYER                 │
├──────────────────────────────────────────────────┤
│ Deduplication │ Standardization │ Conformation │
└────────────┬─────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────┐
│    DIMENSION TABLES (Conformed Data)          │
├──────────────────────────────────────────────────┤
│ dim_date │ dim_team │ dim_player │ dim_referee │
│ dim_stadium │ dim_season                       │
└────────────┬─────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────┐
│      FACT TABLES (Analysis Ready)             │
├──────────────────────────────────────────────────┤
│ fact_match │ fact_match_events │ fact_player...│
└──────────────────────────────────────────────────┘
```

## Database Connection Details

These details are used by the Python application to connect to the Docker container.

| Setting | Environment Variable | Default Value | Docker Service Name |
| :--- | :--- | :--- | :--- |
| **Host** | `MYSQL_HOST` | `localhost` | `epl_mysql` |
| **Port** | `MYSQL_PORT` | `3307` | N/A (Host Port) |
| **User** | `MYSQL_USER` | `root` | `root` |
| **Password** | `MYSQL_PASSWORD` | `1234` | `1234` |
| **Database** | `MYSQL_DB` | `epl_dw` | `epl_dw` |

## Viewing the Database

You can connect to the running `epl_mysql` container using any standard database client (e.g., DBeaver, MySQL Workbench, TablePlus) with the connection details provided above.

**Host:** `localhost`
**Port:** `3307`
**User:** `root`
**Password:** `1234`

## Cleanup

To stop and remove the Docker container and its data (if you didn't use a volume, otherwise it just stops the service):

```bash
docker-compose down
```

To deactivate the virtual environment:

```bash
deactivate
```
