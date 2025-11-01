# ETL Manifest Tracking & Incremental Loading System

## Problem Summary

There were two issues with the previous ETL run:

1. **`--full-etl-and-facts` didn't load fact_match_events on first run**
   - Root cause: Errors in SQL scripts were being silently caught
   - Status: ✅ FIXED - improved error reporting

2. **Why staging tables were being reprocessed**
   - NOT a bug - this is expected behavior when manifest is empty
   - Root cause: We manually cleared `etl_events_manifest` at the start
   - Status: ✅ WORKING AS DESIGNED

## How Manifest Tracking Works

### ETL_Events_Manifest Table
Tracks which StatsBomb matches have been successfully loaded:

```
statsbomb_match_id | file_name | status  | rows_processed | load_start_time
3753972            | 3753972.json | SUCCESS | 3683         | 2025-11-01 15:20:04
3753973            | 3753973.json | SUCCESS | 3478         | 2025-11-01 15:20:08
... (60 matches loaded so far)
```

### How Deduplication Works

When `--full-etl-and-facts` runs:

1. **Check manifest** - For each match JSON file:
   ```python
   SELECT COUNT(*) FROM ETL_Events_Manifest WHERE statsbomb_match_id = :match_id
   ```
   - If found: SKIP (already processed, 0 events returned)
   - If not found: LOAD (process file, insert into staging)

2. **After successful load** - Insert into manifest:
   ```sql
   INSERT INTO ETL_Events_Manifest 
   (statsbomb_match_id, file_name, status, rows_processed)
   VALUES (:match_id, :file_name, 'SUCCESS', :row_count)
   ```

3. **Next run** - Only NEW/UNPROCESSED matches are loaded

### Example: Incremental ETL Runs

**Run 1: Start fresh**
```
Manifest empty: 0 rows
  → Load ALL 380 matches
  → Insert 380 manifest entries (SUCCESS)
  Staging: 1,313,783 events ✅
  Time: ~20-25 minutes
```

**Run 2: Add new matches**
```
Manifest: 380 rows (all SUCCESS)
  → Check each of 380 matches: ALL SKIPPED (manifest hit)
  → Load 0 new events
  Staging: UNCHANGED 1,313,783 events ✅
  Time: ~2 seconds (just checking)
```

**Run 3: Purge manifest + reload**
```
Manifest cleared: 0 rows (via TRUNCATE)
  → Load ALL 380 matches again
  → Insert 380 NEW manifest entries
  Staging: DOUBLED to 2,627,566 events (duplicates!)
  **DANGER: This is why clearing manifest is risky!**
```

## Why You Need to Be Careful with Manifest

### ⚠️ DON'T DO THIS:
```bash
# This will cause DUPLICATE events!
TRUNCATE TABLE etl_events_manifest;  # Loses tracking
python -m src.etl.main --full-etl-and-facts
# Now all 380 matches reload → 2x the events in staging!
```

### ✅ DO THIS FOR CLEAN RELOAD:
```bash
# If you WANT to reload everything fresh:
TRUNCATE TABLE stg_events_raw;       # Clear staging
TRUNCATE TABLE fact_match_events;    # Clear facts
TRUNCATE TABLE etl_events_manifest;  # Lose tracking
TRUNCATE TABLE etl_json_manifest;    # Lose JSON tracking
python -m src.etl.main --full-etl-and-facts
# Fresh load: only one copy of all events
```

### ✅ DO THIS FOR INCREMENTAL LOAD:
```bash
# To only load NEW matches from git repo:
# (Keep manifest intact)
python -m src.etl.main --full-etl-and-facts
# Loads only new matches not in manifest
# Safe, efficient, no duplicates
```

## Current Status

**Staging Events**: 207,605 rows
- Source: 60 matches from StatsBomb
- Manifest tracking: ✅ Working (60 SUCCESS entries)
- Match dates: ✅ Enriched (all 207,605 with match_date)

**Fact Match Events**: 421,018 rows
- Source: Loaded from staging on FIRST manual run
- Then loaded AGAIN on SECOND manual run (duplicates!)
- Should be: 210,509 (need to clean up)

## How to Clean Up Duplicates

```bash
# Truncate and reload once (clean state)
TRUNCATE TABLE fact_match_events;
TRUNCATE TABLE stg_events_raw;

# Keep manifest so it doesn't reload StatsBomb again
# (don't truncate etl_events_manifest)

# Reload just the staging + facts
python -m src.etl.main --load-fact-tables

# Now clean state:
# stg_events_raw: 207,605 (one copy)
# fact_match_events: 210,509 (one copy)
# etl_events_manifest: 60 SUCCESS entries (tracking preserved)
```

## Next Steps

To load MORE matches later:

1. **New data comes into git repo**
   ```bash
   cd data/raw/open-data-master
   git pull  # Gets new match files
   ```

2. **Run incremental ETL**
   ```bash
   # Only NEW matches load (manifest prevents re-processing)
   python -m src.etl.main --full-etl-and-facts
   ```

3. **Result**: Only new events added, no duplicates

## Key Takeaway

✅ **Manifest system prevents duplicate loading**
- It tracks what's already been processed
- Subsequent runs only load new data
- DON'T manually clear manifest unless you want everything to reload
- Always check row counts before/after runs to catch duplicates early
