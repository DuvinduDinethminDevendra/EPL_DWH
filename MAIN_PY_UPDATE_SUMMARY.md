# Main.py Update Summary - Load Fact Tables Command

**Date:** October 26, 2025  
**Version:** 1.1  
**Status:** ✅ Complete

---

## Changes Made

### 1. Updated `src/etl/main.py`

#### New Imports
```python
import subprocess
import os
```

#### New Function: `load_fact_tables()`
- Reads all SQL scripts from `src/sql/` directory
- Executes 6 scripts in order:
  1. `load_fact_match.sql` - Load CSV matches
  2. `load_fact_match_events_step1.sql` - Temp aggregation
  3. `load_fact_match_events_step2.sql` - Mapping verification
  4. `load_fact_match_events_step3_final.sql` - Load 1.36M events
  5. `load_fact_match_events_step4_verify.sql` - Validation
  6. `final_row_count.sql` - Final check
- Handles errors gracefully with rollback
- Displays progress and results in real-time

#### Updated Argument Parser
```python
parser.add_argument("--load-fact-tables", action="store_true", 
                   help="Load fact tables from staging data (run after --full-etl)")
```

#### Updated Main Function
- Added routing for `--load-fact-tables` flag
- Calls `load_fact_tables()` when flag is used

### 2. New Documentation File: `LOAD_FACT_TABLES_GUIDE.md`

Comprehensive guide including:
- Command usage and syntax
- What each script does
- Complete ETL workflow
- Command reference table
- Output example
- Error handling
- Troubleshooting

### 3. Updated README.md

- Added usage examples section
- Updated Alternative Commands
- Added link to LOAD_FACT_TABLES_GUIDE.md
- Documented the new `--load-fact-tables` command

---

## Usage

### Simple Two-Step Process

```powershell
# Step 1: Extract and load dimensions
python -m src.etl.main --full-etl

# Step 2: Load fact tables
python -m src.etl.main --load-fact-tables
```

### Advanced: Step-by-Step

```powershell
# Manual step control if needed
python -m src.etl.main --staging
python -m src.etl.main --warehouse
python -m src.etl.main --load-fact-tables
```

---

## Available Commands (Complete Reference)

| Command | Purpose | Time |
|---------|---------|------|
| `--test-db` | Test DB connectivity | 1s |
| `--full-etl` | Staging + Dimensions | 5-10 min |
| `--staging` | Staging only | 2-5 min |
| `--warehouse` | Dimensions only | 2-3 min |
| **`--load-fact-tables`** | **Fact tables** | **~12 min** |

---

## What Gets Loaded

### fact_match (830 rows)
- CSV match data with dimension keys
- Teams, dates, referees, stadiums, seasons
- Match results and metadata

### fact_match_events (1,362,577 rows)
- Individual match events from StatsBomb
- Event types: Pass, Shot, Duel, etc.
- Player and team references
- Minute and extra time info

### Verification
- Event type distribution
- Player and team coverage
- Overall row counts by table

---

## Error Handling

The `load_fact_tables()` function includes:
- File existence checks
- Statement-level error handling
- Transaction rollback on failure
- Graceful error messages
- Detailed progress tracking

Example error output:
```
[WARNING] Script not found: C:\path\to\script.sql
[ERROR] Statement 3 failed: Cannot add or update a child row
```

---

## Integration Points

The new command integrates with:
- **Database connection:** Uses existing `get_engine()` from `src.etl.db`
- **Path resolution:** Finds SQL scripts via `Path(__file__)`
- **Error handling:** Uses SQLAlchemy for connection and transaction management
- **Logging:** Prints progress to console

---

## Benefits

✅ **One-command fact loading** - No need to run 6 SQL scripts manually  
✅ **Automated sequencing** - Scripts run in correct order automatically  
✅ **Error recovery** - Failed statements don't cascade  
✅ **Progress tracking** - See what's happening in real-time  
✅ **Result display** - Shows verification results directly  
✅ **Integrates seamlessly** - Works with existing `--full-etl` command

---

## Testing

To verify the implementation:

```powershell
# Test help message
python -m src.etl.main --help

# Should show:
# --load-fact-tables    Load fact tables from staging data (run after --full-etl)

# Test execution (after --full-etl)
python -m src.etl.main --load-fact-tables

# Should output:
# ================================================================================
# LOADING FACT TABLES FROM STAGING DATA
# ================================================================================
# [1/6] Load fact_match from CSV (830 matches)
#   Executing: load_fact_match.sql
#   → (830,)
# ...
# ✅ FACT TABLE LOADING COMPLETED SUCCESSFULLY
```

---

## Files Modified

| File | Changes |
|------|---------|
| `src/etl/main.py` | Added imports, new function, argument parser update |
| `README.md` | Added usage examples and command reference |

## Files Created

| File | Purpose |
|------|---------|
| `LOAD_FACT_TABLES_GUIDE.md` | Complete user guide |
| `MAIN_PY_UPDATE_SUMMARY.md` | This file |

---

## Next Steps

1. ✅ Code updated and ready
2. ✅ Documentation complete
3. Ready for git commit:

```bash
git add src/etl/main.py
git add README.md
git add LOAD_FACT_TABLES_GUIDE.md
git add MAIN_PY_UPDATE_SUMMARY.md

git commit -m "feat: Add --load-fact-tables command for convenient fact table loading

- Adds new --load-fact-tables CLI argument
- Automatically executes 6 SQL scripts in sequence
- Loads fact_match (830 rows) and fact_match_events (1.36M rows)
- Handles errors with transaction rollback
- Provides progress tracking and result display
- See LOAD_FACT_TABLES_GUIDE.md for usage details"

git push origin main
```

---

**Status:** ✅ Ready for production  
**Last Updated:** October 26, 2025
