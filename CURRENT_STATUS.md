# EPL DWH - Current Status & Execution Guide

**Last Updated:** 2025-10-25  
**Status:** ✓ Active - ETL Pipeline Running  
**Extraction Progress:** 62/380 EPL matches (16.3%) | ~214k events loaded

---

## Quick Start

### Run Full ETL Pipeline (Recommended)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Execute full ETL: Extract → Transform → Load
python -m src.etl.main --full-etl
```

This single command will:
1. ✓ Clone/update StatsBomb repository
2. ✓ Filter 3,464 event files → 380 EPL-only files
3. ✓ Load all 380 EPL matches into staging tables
4. ✓ Populate dimension tables (teams, players, referees, dates, stadiums, seasons)
5. ✓ Load fact tables (fact_match, fact_match_events, fact_player_stats)

### Alternative Commands
```bash
# Test database connection only
python -m src.etl.main --test-db

# Load dimensions only
python -m src.etl.main --warehouse

# Monitor extraction progress (in separate terminal)
python monitor_etl.py
```

---

## Project Structure

```
EPL_DWH/
├── src/
│   ├── etl/
│   │   ├── main.py              # ← Entry point (use python -m src.etl.main)
│   │   ├── extract/
│   │   │   └── statsbomb_reader.py  # EPL-only filter + event extraction
│   │   ├── transform/
│   │   │   └── *.py             # Dimension cleaning & upserts
│   │   ├── load/
│   │   │   └── load_facts.py    # Fact table loading
│   │   └── db.py                # Database connection
│   ├── sql/
│   │   ├── create_schema.sql    # Database schema definition
│   │   └── load_fact_match_events.sql
│   └── utils/
│       ├── logger.py
│       └── dq_checks.py
├── data/
│   ├── raw/
│   │   ├── open-data-master/    # StatsBomb open data (cloned from GitHub)
│   │   └── csv/                 # Match/player/team CSVs
│   └── staging/
├── docker-compose.yml           # MySQL 8.0 + initialization
├── requirements.txt             # Python dependencies
├── monitor_etl.py              # Progress monitor script
├── run_full_etl.py             # Legacy wrapper (use --full-etl instead)
└── [README, DELIVERY_DOCUMENT, EXTRACTION_IMPROVEMENTS].md
```

---

## Current Data Status

### Extraction Progress
| Metric | Value |
|--------|-------|
| **EPL Matches Available** | 380 (2015-16 season) |
| **Matches Processed** | 62 (16.3%) |
| **Events Loaded** | 214,559 |
| **Average Events/Match** | 3,460 |
| **Est. Total Events** | ~1.3M (at completion) |
| **Estimated ETA** | ~20 minutes |

### Database Tables
- ✓ **21 tables** created in `epl_dw` schema
- ✓ **Staging tables** ready (stg_events_raw, ETL_Events_Manifest)
- ✓ **Dimension tables** ready (dim_team, dim_player, dim_referee, etc.)
- ✓ **Fact tables** ready (fact_match, fact_match_events, fact_player_stats)

### EPL Data Filtering
- **Source Files:** 3,464 total StatsBomb event JSONs (all competitions)
- **Filtered to EPL:** 380 files (2015-16 season only)
- **Filtering Mechanism:** 
  - Read official match IDs from `data/matches/2/27.json` (EPL season 27)
  - Filter event files by match_id ∈ EPL_match_ids set
  - **Result:** 100% EPL-only, zero non-EPL data

---

## Key Improvements (v2)

### 1. EPL-Only Filtering
**File:** `src/etl/extract/statsbomb_reader.py`

- Added `get_epl_match_ids()` function
- Updated `get_epl_events_files()` to filter from 3,464 → 380 files
- **Benefit:** 88.7% reduction in file processing, zero non-EPL data

### 2. Per-File Transaction Isolation
**File:** `src/etl/extract/statsbomb_reader.py`

- `load_events_from_file()` now uses `engine.begin()` context manager
- Each file has isolated transaction: success commits, failure rolls back
- Smaller chunksize (500 → 250) for better connection pool management
- **Benefit:** Eliminated "Can't reconnect" errors, improved reliability

### 3. Unified Entry Point
**File:** `src/etl/main.py`

- Single command: `python -m src.etl.main --full-etl`
- Orchestrates entire pipeline: extract → transform → load
- **Benefit:** No need to run multiple scripts separately

---

## Recent Work

### Database Recreation (2025-10-25 19:49)
```bash
# Recreated clean schema
docker cp src/sql/create_schema.sql epl_mysql:/tmp/
docker exec epl_mysql mysql -u root -p1234 < /tmp/create_schema.sql

# Verified: 21 tables created, staging tables empty
```

### ETL Pipeline Start (2025-10-25 19:49)
```bash
python -m src.etl.main --full-etl

# Output:
# ✓ 380 EPL Match IDs identified
# ✓ 380 EPL Event files filtered
# ✓ Extraction started, running smoothly
# ✓ Progress: 62/380 (16.3%), ~214k events
```

---

## Next Steps

### 1. Wait for Extraction Completion
- Estimated: 15-20 minutes remaining
- Monitor progress: `python monitor_etl.py` (in separate terminal)
- Expected final state: 380 matches, ~1.3M-1.4M events in `stg_events_raw`

### 2. Verify Extraction (After Completion)
```bash
python -c "
from src.etl.db import get_engine
from sqlalchemy import text
engine = get_engine()
conn = engine.connect()
m = conn.execute(text('SELECT COUNT(*) FROM ETL_Events_Manifest')).scalar()
e = conn.execute(text('SELECT COUNT(*) FROM stg_events_raw')).scalar()
print(f'Matches: {m}, Events: {e:,}')
"
```

### 3. Fact Table Population
The `--full-etl` flag will automatically load fact tables after extraction completes.
If needed, run manually:
```bash
python -m src.etl.main --warehouse
```

### 4. Data Quality Checks
```bash
# Check for orphaned records (no FK match)
SELECT COUNT(*) FROM fact_match_events WHERE player_id = -1
SELECT COUNT(*) FROM fact_match_events WHERE team_id = -1
```

---

## Troubleshooting

### Pipeline Stalls or Errors
1. Check logs in terminal output
2. Verify database connection: `python -m src.etl.main --test-db`
3. Clear staging and restart:
   ```bash
   docker exec epl_mysql mysql -u root -p1234 -e "
   USE epl_dw;
   TRUNCATE TABLE stg_events_raw;
   TRUNCATE TABLE ETL_Events_Manifest;
   "
   python -m src.etl.main --full-etl
   ```

### Database Issues
```bash
# Connect directly to MySQL
docker exec -it epl_mysql mysql -u root -p1234 epl_dw

# Show table row counts
SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'epl_dw' ORDER BY TABLE_NAME;
```

---

## Files Modified / Created

### Core Code Changes
- ✓ `src/etl/extract/statsbomb_reader.py` - EPL filter + transaction isolation
- ✓ `src/etl/main.py` - Unified entry point with `--full-etl` flag

### Documentation
- ✓ `EXTRACTION_IMPROVEMENTS.md` - Technical details of v2 improvements
- ✓ `CURRENT_STATUS.md` - This file
- ✓ `README.md` - (to be updated)

### Cleanup
- ✓ Removed 7 temporary test scripts

---

## Git Status
```bash
git status
# Modified files: src/etl/extract/statsbomb_reader.py
#                src/etl/main.py
# New files:     EXTRACTION_IMPROVEMENTS.md
#                CURRENT_STATUS.md
```

To commit:
```bash
git add src/etl/extract/statsbomb_reader.py src/etl/main.py
git add EXTRACTION_IMPROVEMENTS.md CURRENT_STATUS.md
git commit -m "feat: EPL-only filtering + per-file transactions + unified --full-etl entry point"
git push
```

---

## Contact & Support
For issues or questions about the pipeline, refer to:
- `EXTRACTION_IMPROVEMENTS.md` - Technical architecture
- `README.md` - General project information
- `src/etl/main.py` - Entry point documentation
