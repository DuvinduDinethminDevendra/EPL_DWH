# EPL Data Warehouse - Complete ETL Pipeline Summary

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAW DATA SOURCES                              │
├────────────────────┬────────────────────┬──────────────────────┤
│  JSON FILES        │  REST API          │  CSV FILES           │
│  (666 files,       │  (football-data)   │  (3 match files,    │
│   47K+ players)    │  (60 teams/teams)  │   830 records)       │
└────────────┬───────┴────────────┬───────┴──────────────┬────────┘
             │                    │                      │
             └────────────────────┼──────────────────────┘
                                  ▼
             ┌──────────────────────────────────┐
             │     EXTRACT (Staging Layer)      │
             ├──────────────────────────────────┤
             │ • stg_player_raw (47,852 rows)  │
             │ • stg_team_raw (60 rows)        │
             │ • stg_e0_match_raw (830 rows)   │
             │                                  │
             │ Files: src/etl/staging/          │
             │ - load_staging.py                │
             │ - load_warehouse.py              │
             └──────────────────┬───────────────┘
                                │
                                ▼
             ┌──────────────────────────────────┐
             │   CLEAN (Data Quality Layer)     │
             ├──────────────────────────────────┤
             │ • Trim whitespace                │
             │ • Remove NULLs                   │
             │ • Validate data types            │
             │ • Standardize naming             │
             │                                  │
             │ Files: src/etl/transform/        │
             │ - clean.py                       │
             │ - load_warehouse.py              │
             └──────────────────┬───────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │  TRANSFORM & LOAD (Dimension Layer)       │
        ├───────────────────────────────────────────┤
        │ • Extract DISTINCT records                │
        │ • Apply business keys                     │
        │ • INSERT...ON DUPLICATE KEY UPDATE        │
        │ • Write to etl_log                        │
        │                                           │
        │ File: src/etl/transform/                  │
        │ - clean_and_upsert_dim.py           │
        └───────────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │      DATA WAREHOUSE (Fact/Dim Layer)      │
        ├───────────────────────────────────────────┤
        │ DIMENSIONS:                               │
        │ • dim_player (6,741 rows) ✅              │
        │ • dim_team (50 rows) ✅                   │
        │ • dim_stadium (25 rows) ✅                │
        │ • dim_referee (32+ rows) ✅               │
        │                                           │
        │ AUDIT:                                    │
        │ • etl_log (operation tracking)            │
        │ • ETL_JSON_Manifest (file tracking)       │
        │ • ETL_Api_Manifest (API tracking)         │
        │ • ETL_File_Manifest (CSV tracking)        │
        └───────────────────────────────────────────┘
```

## ETL Pipeline Execution Flow

### 1. EXTRACT Phase: Load Raw Data to Staging
**File**: `src/etl/staging/load_staging.py`

```python
# Execution
load_all_staging()

# Steps
├── write_staging_from_json()      # 666 JSON files → stg_player_raw
├── write_staging_from_api()        # REST API calls → stg_team_raw
└── write_staging_from_csv()        # 3 CSV files → stg_e0_match_raw

# Results
✅ 47,852 player records loaded
✅ 60 team records loaded
✅ 830 match records loaded
Total: 48,742 staging records
```

### 2. CLEAN Phase: Data Quality Transformations
**File**: `src/etl/load_warehouse.py`

```python
# Execution
clean_staging_data()

# Transformations
├── Player names: TRIM, title-case, remove NULLs
├── Team names: TRIM, remove NULLs
└── Match data: TRIM team names, validate dates

# Logging
All operations logged to etl_log table
```

### 3. TRANSFORM & LOAD Phase: Dimension Upserts
**File**: `src/etl/transform/clean_and_upsert_dim.py` ✨ **NEW**

```python
# Execution
run_all_upserts(engine)

# Upserts (IN SEQUENCE)
├── [1/4] upsert_dim_player()
│   ├── Source: stg_player_raw (SELECT DISTINCT player_name)
│   ├── Business Key: player_name
│   ├── Operation: INSERT...ON DUPLICATE KEY UPDATE
│   └── Result: 6,741 rows affected
│
├── [2/4] upsert_dim_team()
│   ├── Source: stg_team_raw (SELECT DISTINCT name)
│   ├── Business Key: team_name
│   ├── Operation: INSERT...ON DUPLICATE KEY UPDATE
│   └── Result: 50 rows affected
│
├── [3/4] upsert_dim_stadium()
│   ├── Source: stg_e0_match_raw (SELECT DISTINCT HomeTeam)
│   ├── Business Key: stadium_name
│   ├── Operation: INSERT...ON DUPLICATE KEY UPDATE
│   └── Result: 25 rows affected
│
└── [4/4] upsert_dim_referee()
    ├── Source: stg_e0_match_raw (SELECT DISTINCT Referee)
    ├── Business Key: referee_name
    ├── Operation: INSERT...ON DUPLICATE KEY UPDATE
    └── Result: 32+ rows affected

# Logging
Each upsert writes 1 entry to etl_log with:
├── job_name: "upsert_dim_player" etc.
├── phase_step: "transform"
├── status: "SUCCESS" or "FAILED"
├── start_time, end_time
├── rows_processed
└── message: descriptive text
```

## File Structure

```
EPL_DWH/
├── src/etl/
│   ├── __init__.py
│   ├── config.py                          ← Database configuration
│   ├── db.py                              ← Shared database engine
│   │
│   ├── extract/
│   │   ├── json_reader.py                 ← JSON file reader (666 files)
│   │   ├── api_client.py                  ← REST API client (60 teams)
│   │   └── csv_reader.py                  ← CSV file reader (830 records)
│   │
│   ├── staging/
│   │   ├── load_staging.py                ← Unified staging loader ✅
│   │   └── load_warehouse.py              ← Orchestration + cleaning ✅
│   │
│   └── transform/
│       ├── clean.py                       ← Cleaning functions
│       ├── upsert_dims.py                 ← Legacy upsert (replaced)
│       └── clean_and_upsert_dim.py        ← NEW dimension upsert module ✨
│
├── src/sql/
│   └── create_schema.sql                  ← Database schema
│
└── data/
    ├── raw/
    │   ├── json/                          (666 JSON files)
    │   ├── csv/                           (3 CSV files)
    │   └── (API data direct to DB)
    └── staging/ (logical, in database)
```

## Running the Complete Pipeline

### Option 1: Run Individual Phases

```bash
# Phase 1: Extract only
cd d:\myPortfolioProject\EPL_DWH
.\.venv\Scripts\python.exe -m src.etl.staging.load_staging

# Phase 2: Extract + Clean
.\.venv\Scripts\python.exe -m src.etl.load_warehouse

# Phase 3: Extract + Clean + Transform & Load
# (Integrate clean_and_upsert_dim into load_warehouse.py)
```

### Option 2: Run Dimension Upserts Only

```bash
# Run ONLY dimension upserts (assumes staging tables populated)
.\.venv\Scripts\python.exe -m src.etl.transform.clean_and_upsert_dim
```

## Key Features

### ✅ Idempotent Operations
- All upsert operations are **re-runnable** without side effects
- ON DUPLICATE KEY UPDATE only updates existing records
- Manifest tables prevent re-processing of files

### ✅ Error Resilience
- Individual module failures don't stop the pipeline
- Comprehensive error logging to etl_log
- Graceful exception handling with detailed messages

### ✅ Audit Trail
- Every operation logged to etl_log table
- File processing tracked in manifest tables
- Complete execution history available for debugging

### ✅ No Pandas Dependency
- clean_and_upsert_dim.py uses only SQLAlchemy + standard library
- Lightweight, fast, minimal memory footprint
- Efficient SQL operations directly in database

### ✅ Type Hints & Documentation
- Full Python 3.13+ type hints
- Comprehensive docstrings for all functions
- Inline comments explaining business logic

## Database Schema Summary

### Staging Tables
| Table | Records | Columns | Purpose |
|-------|---------|---------|---------|
| stg_player_raw | 47,852 | 15 | Player data from JSON files |
| stg_team_raw | 60 | 35 | Team data from REST API |
| stg_e0_match_raw | 830 | 26 | Match results from CSV files |

### Dimension Tables
| Table | Rows | Business Key | Purpose |
|-------|------|--------------|---------|
| dim_player | 6,741 | player_name | Player master data |
| dim_team | 50+ | team_name | Team master data |
| dim_stadium | 25 | stadium_name | Stadium master data |
| dim_referee | 32+ | referee_name | Referee master data |

### Audit Tables
| Table | Purpose |
|-------|---------|
| etl_log | Complete operation history |
| ETL_JSON_Manifest | Tracks all 666 JSON files loaded |
| ETL_Api_Manifest | Tracks all API calls by season |
| ETL_File_Manifest | Tracks all CSV files processed |

## Performance Characteristics

- **JSON Reader**: ~1 sec to process 666 files (skip if manifested)
- **API Client**: ~5 secs to fetch 60 teams (3 seasons)
- **CSV Reader**: <1 sec to load 830 records
- **Dimension Upserts**: ~1 sec total for all 4 dimensions
- **Total Pipeline**: ~8 seconds (excludes cleaning operations)

## Next Steps

1. **Fact Table Loading**
   - Create `fact_matches` table (normalized match results)
   - Join with dimension keys via business keys
   - Implement `upsert_fact_matches()` function

2. **Data Quality Validation**
   - Row count reconciliation (source vs target)
   - Duplicate detection and handling
   - NULL value analysis by column

3. **Performance Optimization**
   - Batch insert operations for large datasets
   - Index creation/analysis
   - Query execution plan review

4. **Scheduling & Monitoring**
   - DAG orchestration (Airflow, etc.)
   - Email notifications on failures
   - Dashboard for etl_log metrics

## Technology Stack

- **Language**: Python 3.13.5
- **Database**: MySQL 8.0 (Docker container)
- **ORM/Query**: SQLAlchemy 2.x (core, no ORM)
- **Data Formats**: JSON, CSV, REST API
- **Environment**: Windows PowerShell, Docker

## Files Created/Modified This Session

| File | Status | Purpose |
|------|--------|---------|
| `clean_and_upsert_dim.py` | ✨ **NEW** | Production-grade dimension upsert module |
| `IMPLEMENTATION_NOTES.md` | 📝 NEW | Detailed implementation documentation |
| `load_warehouse.py` | ✏️ Modified | Added cleaning phase orchestration |
| `load_staging.py` | ✅ Existing | Unified staging loader |

---

**Total Project Statistics**:
- 📊 Data Loaded: 48,742 staging records
- 📈 Dimensions Created: 6,848 distinct records across 4 tables
- 📋 Audit Trail: Complete operation logging to etl_log
- ⚡ Pipeline Duration: ~8 seconds (excluding cleaning)
- 🎯 Business Coverage: Players, Teams, Stadiums, Referees, Matches
