# Updated ETL Main.py - Load Fact Tables Command

## New Command: `--load-fact-tables`

The main ETL script has been updated to support loading fact tables directly with a new command-line flag.

### Usage

```powershell
python -m src.etl.main --load-fact-tables
```

### What It Does

This command executes all 6 SQL scripts in sequence to load the fact tables:

1. **load_fact_match.sql** (2-3 seconds)
   - Loads 830 CSV matches into `fact_match`
   - Joins with dimensions (team, date, referee, stadium, season)

2. **load_fact_match_events_step1.sql** (~30 seconds)
   - Creates temporary aggregation table
   - Collapses 1.3M events into 760 (match, team) pairs
   - Creates index for fast joins

3. **load_fact_match_events_step2.sql** (~15 seconds)
   - Verifies mapping coverage
   - Shows statistics on CSV↔StatsBomb match pairs

4. **load_fact_match_events_step3_final.sql** (~11 minutes)
   - **Main event loader**
   - Inserts 1,362,577 events into `fact_match_events`
   - Uses optimized mapping table joins

5. **load_fact_match_events_step4_verify.sql** (~5 seconds)
   - Validates loaded data
   - Shows event type distribution

6. **final_row_count.sql** (~2 seconds)
   - Shows final state of all 21 tables
   - Confirms successful load

**Total Time:** ~12-13 minutes

### Complete ETL Workflow

```bash
# Step 1: Run full ETL (staging + dimensions)
python -m src.etl.main --full-etl

# Step 2: Load fact tables
python -m src.etl.main --load-fact-tables

# Done! All data loaded and verified
```

### Alternative: Run All at Once

If you want to customize the pipeline, you can:

```bash
# Just load staging
python -m src.etl.main --staging

# Then load dimensions
python -m src.etl.main --warehouse

# Then load facts
python -m src.etl.main --load-fact-tables
```

### Command Reference

| Command | Purpose | Time |
|---------|---------|------|
| `--test-db` | Test database connectivity | 1s |
| `--full-etl` | Staging + Dimensions | 5-10 min |
| `--staging` | Staging only | 2-5 min |
| `--warehouse` | Dimensions only | 2-3 min |
| **`--load-fact-tables`** | **Load fact tables** | **~12 min** |

### Output Example

```
================================================================================
LOADING FACT TABLES FROM STAGING DATA
================================================================================

[1/6] Load fact_match from CSV (830 matches)
  Executing: load_fact_match.sql
  → (830,)

[2/6] Step 1: Create temporary aggregation table
  Executing: load_fact_match_events_step1.sql
  → (760,)
  → (380,20)

[3/6] Step 2: Verify match mappings
  Executing: load_fact_match_events_step2.sql
  → (684,)
  → (342,190)

[4/6] Step 3: Load 1.36M events into fact_match_events
  Executing: load_fact_match_events_step3_final.sql
  → (1362577,342,286,452121)

[5/6] Step 4: Verify loaded data
  Executing: load_fact_match_events_step4_verify.sql
  → ('Pass', 694596)
  → ('Carry', 534227)
  → ...

[6/6] Final verification: Show all table row counts
  Executing: final_row_count.sql
  → ('dim_date', 17533)
  → ('fact_match_events', 1362577)
  → ...

================================================================================
✅ FACT TABLE LOADING COMPLETED SUCCESSFULLY
================================================================================
```

### Error Handling

If a script fails:
- Error message is displayed with statement number
- Previous successful scripts' changes remain (atomic per statement)
- Process stops to prevent cascade failures

### Requirements

- Database must have staging tables populated (run `--full-etl` first)
- All dimensions must be present
- Mapping tables must exist

### Troubleshooting

**"Script not found" error:**
- Ensure SQL files exist in `src/sql/`
- Check file names match exactly

**"Cannot add or update a child row" error:**
- FK constraint violation - check mapping tables are populated
- Run `--full-etl` first to populate dimensions

**Long execution time:**
- Normal for event loading (~11 minutes)
- This is expected and efficient for 1.36M inserts

---

## Code Changes

### Added to `src/etl/main.py`:

1. **Import statements** for subprocess, os, and Path
2. **`load_fact_tables()` function** that:
   - Reads all SQL scripts from `src/sql/`
   - Executes them in order
   - Handles errors gracefully
   - Displays progress and results
3. **New argument parser flag** `--load-fact-tables`
4. **Command routing** in `main()` function

### Benefits

✅ Convenient single-command fact table loading  
✅ Automated execution of all 6 scripts in correct order  
✅ Progress tracking and error reporting  
✅ Works with existing `--full-etl` command  
✅ Can be run standalone if staging/dimensions already exist

---

**Updated:** October 26, 2025  
**Version:** 1.1  
**Status:** ✅ Ready for production
