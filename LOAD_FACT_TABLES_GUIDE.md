# Load Fact Tables Guide# Updated ETL Main.py - Load Fact Tables Command



Detailed instructions for loading fact tables from staging data using the `--load-fact-tables` command.## New Command: `--load-fact-tables`



---The main ETL script has been updated to support loading fact tables directly with a new command-line flag.



## 📋 Quick Start### Usage



```powershell```powershell

# Step 1: Ensure database is runningpython -m src.etl.main --load-fact-tables

docker-compose up -d```



# Step 2: Activate Python environment### What It Does

.\.venv\Scripts\Activate.ps1

This command executes all 6 SQL scripts in sequence to load the fact tables:

# Step 3: Run complete ETL first (required!)

python -m src.etl.main --full-etl1. **load_fact_match.sql** (2-3 seconds)

   - Loads 830 CSV matches into `fact_match`

# Step 4: Load fact tables   - Joins with dimensions (team, date, referee, stadium, season)

python -m src.etl.main --load-fact-tables

```2. **load_fact_match_events_step1.sql** (~30 seconds)

   - Creates temporary aggregation table

**Total time:** ~20 minutes   - Collapses 1.3M events into 760 (match, team) pairs

   - Creates index for fast joins

---

3. **load_fact_match_events_step2.sql** (~15 seconds)

## When to Use `--load-fact-tables`   - Verifies mapping coverage

   - Shows statistics on CSV↔StatsBomb match pairs

### ✅ Use this command when:

- Staging tables are already populated (`stg_events_raw` has data)4. **load_fact_match_events_step3_final.sql** (~11 minutes)

- Dimensions are already created (`dim_team`, `dim_player`, etc.)   - **Main event loader**

- You only need to load the fact tables   - Inserts 1,362,577 events into `fact_match_events`

- You want to reload facts without recreating dimensions   - Uses optimized mapping table joins



### ❌ Don't use this command if:5. **load_fact_match_events_step4_verify.sql** (~5 seconds)

- Database is empty (no staging or dimensions)   - Validates loaded data

- First-time setup (use `--full-etl` instead)   - Shows event type distribution

- You're unsure about data state (run `--test-db` first)

6. **final_row_count.sql** (~2 seconds)

---   - Shows final state of all 21 tables

   - Confirms successful load

## What Gets Loaded

**Total Time:** ~12-13 minutes

The `--load-fact-tables` command loads **4 key outputs**:

### Complete ETL Workflow

### 1. **Mapping Tables** (Required)

```bash

#### dim_team_mapping# Step 1: Run full ETL (staging + dimensions)

- Maps StatsBomb team IDs → dim_team IDspython -m src.etl.main --full-etl

- 40 rows (17 EPL teams + 7 international → -1)

- Fixes team ID translation issues# Step 2: Load fact tables

python -m src.etl.main --load-fact-tables

```sql

SELECT COUNT(*) FROM dim_team_mapping;# Done! All data loaded and verified

-- Result: 40 rows```

```

### Alternative: Run All at Once

#### dim_match_mapping

- Maps CSV match IDs → StatsBomb match IDsIf you want to customize the pipeline, you can:

- 684 rows (one-to-one match pairs)

- Enables joining CSV facts with StatsBomb events```bash

# Just load staging

```sqlpython -m src.etl.main --staging

SELECT COUNT(*) FROM dim_match_mapping;

-- Result: 684 rows# Then load dimensions

```python -m src.etl.main --warehouse



---# Then load facts

python -m src.etl.main --load-fact-tables

### 2. **fact_match** (830 rows)```



Match-level facts from CSV data:### Command Reference

- Match date, teams, score, attendance

- Venue, referee, half-time score| Command | Purpose | Time |

- Direct load from CSV source|---------|---------|------|

| `--test-db` | Test database connectivity | 1s |

```sql| `--full-etl` | Staging + Dimensions | 5-10 min |

SELECT COUNT(*) FROM fact_match;| `--staging` | Staging only | 2-5 min |

-- Result: 830 rows| `--warehouse` | Dimensions only | 2-3 min |

```| **`--load-fact-tables`** | **Load fact tables** | **~12 min** |



---### Output Example



### 3. **fact_match_events** (1,362,577 rows)```

================================================================================

Event-level facts from StatsBomb:LOADING FACT TABLES FROM STAGING DATA

- Event type (pass, shot, foul, etc.)================================================================================

- Player involved, minute, location

- Match context and outcome[1/6] Load fact_match from CSV (830 matches)

  Executing: load_fact_match.sql

```sql  → (830,)

SELECT COUNT(*) FROM fact_match_events;

-- Result: 1,362,577 rows[2/6] Step 1: Create temporary aggregation table

```  Executing: load_fact_match_events_step1.sql

  → (760,)

Example events per match:  → (380,20)

- **Arsenal vs Bournemouth:** 3,487 events

- **Chelsea vs Everton:** 4,102 events[3/6] Step 2: Verify match mappings

- **Average:** ~3,900 events/match  Executing: load_fact_match_events_step2.sql

  → (684,)

---  → (342,190)



### 4. **Verification Data**[4/6] Step 3: Load 1.36M events into fact_match_events

  Executing: load_fact_match_events_step3_final.sql

After loading, verification queries run:  → (1362577,342,286,452121)

- Row count checks

- Foreign key validation[5/6] Step 4: Verify loaded data

- Data quality metrics  Executing: load_fact_match_events_step4_verify.sql

  → ('Pass', 694596)

---  → ('Carry', 534227)

  → ...

## Command Output Explained

[6/6] Final verification: Show all table row counts

### Step 0: Populate Mapping Tables  Executing: final_row_count.sql

  → ('dim_date', 17533)

```  → ('fact_match_events', 1362577)

[STEP 0] Populating mapping tables...  → ...

  

================================================================================================================================================================

POPULATING MAPPING TABLES✅ FACT TABLE LOADING COMPLETED SUCCESSFULLY

================================================================================================================================================================

```

Executing 11 SQL statements...

### Error Handling

Mapping:  36%|#  | 4/11 [00:29<00:51,  7.33s/stmt]  ✓ (24,)

  ✓ (24,)If a script fails:

Mapping:  73%|##1| 8/11 [00:29<00:09,  3.04s/stmt]  ✓ (380,)- Error message is displayed with statement number

  ✓ (380,)- Previous successful scripts' changes remain (atomic per statement)

Mapping: 100%|##| 11/11 [00:29<00:00,  2.68s/stmt]- Process stops to prevent cascade failures



✅ Mapping tables populated successfully!### Requirements

```

- Database must have staging tables populated (run `--full-etl` first)

**What it means:**- All dimensions must be present

- 11 SQL statements executed- Mapping tables must exist

- 24 team mappings created

- 380 match mappings created### Troubleshooting

- All completed in ~29 seconds

**"Script not found" error:**

---- Ensure SQL files exist in `src/sql/`

- Check file names match exactly

### Step 1: Load fact_match

**"Cannot add or update a child row" error:**

```- FK constraint violation - check mapping tables are populated

▶ [1/6] Load fact_match from CSV (830 matches)- Run `--full-etl` first to populate dimensions



Overall Progress:  17%|######3                               | 1/6 [00:00<00:01,  4.57stmt/s] **Long execution time:**

→ (Decimal('0'), Decimal('0'), 0)- Normal for event loading (~11 minutes)

```- This is expected and efficient for 1.36M inserts



**What it means:**---

- 830 matches loaded from CSV

- Took ~1 second## Code Changes

- Initial check shows no data issues (0 problems, 0 warnings)

### Added to `src/etl/main.py`:

---

1. **Import statements** for subprocess, os, and Path

### Step 3: Load fact_match_events2. **`load_fact_tables()` function** that:

   - Reads all SQL scripts from `src/sql/`

```   - Executes them in order

▶ [3/6] Step 2: Verify match mappings   - Handles errors gracefully

   - Displays progress and results

→ (380, 380)atch_events_step2.sql:  25%|#####               | 1/4 [00:28<01:24, 28.13s/stmt]3. **New argument parser flag** `--load-fact-tables`

4. **Command routing** in `main()` function

▶ [4/6] Step 3: Load 1.36M events into fact_match_events

### Benefits

Overall Progress:  67%|########################6            | 4/6 [07:34<04:39, 139.84s/script]

```✅ Convenient single-command fact table loading  

✅ Automated execution of all 6 scripts in correct order  

**What it means:**✅ Progress tracking and error reporting  

- Match verification passed: 380 CSV matches → 380 StatsBomb matches✅ Works with existing `--full-etl` command  

- 1.36M events inserted successfully✅ Can be run standalone if staging/dimensions already exist

- Took ~139 seconds (2-3 minutes)

---

---

**Updated:** October 26, 2025  

### Final Status**Version:** 1.1  

**Status:** ✅ Ready for production

```
================================================================================
✅ FACT TABLE LOADING COMPLETED SUCCESSFULLY (459.66s)
================================================================================
```

**Summary:**
- All 6 steps completed without errors
- Total time: ~459 seconds (~7-8 minutes)
- 1,362,577 events + 830 matches loaded
- All FK constraints satisfied

---

## Troubleshooting Common Issues

### Issue 1: "Table Does Not Exist"

**Error:**
```
1146 (42S02): Table 'epl_dw.stg_events_raw' doesn't exist
```

**Cause:** Staging tables don't exist (not populated)

**Solution:**
```powershell
# Run full ETL first
python -m src.etl.main --full-etl

# Then run fact tables
python -m src.etl.main --load-fact-tables
```

---

### Issue 2: "Foreign Key Constraint Failed"

**Error:**
```
1452 (23000): Cannot add or update child row: foreign key constraint fails
```

**Cause:** Dimension table missing a required value

**Solution:**
1. Check which dimension failed
2. Verify dimensions were created: `SELECT COUNT(*) FROM dim_team;`
3. Recreate dimensions: `python -m src.etl.main --warehouse`
4. Retry fact loading: `python -m src.etl.main --load-fact-tables`

---

### Issue 3: "Duplicate Entry"

**Error:**
```
1062 (23000): Duplicate entry '1' for key 'PRIMARY'
```

**Cause:** Fact table already has this data (re-running without clearing)

**Solution:**
```powershell
# Clear fact tables
docker exec epl_mysql mysql -u root -p1234 epl_dw -e "
TRUNCATE TABLE fact_match_events;
TRUNCATE TABLE fact_match;
TRUNCATE TABLE dim_match_mapping;
TRUNCATE TABLE dim_team_mapping;
"

# Retry
python -m src.etl.main --load-fact-tables
```

---

### Issue 4: Connection Lost During Long Load

**Error:**
```
2006 (HY000): MySQL server has gone away
```

**Cause:** Long-running query timed out

**Solution:**
1. Increase MySQL timeout: Edit `docker-compose.yml`
2. Reduce chunk size: Edit `src/etl/main.py` (line 250)
3. Run on faster machine

---

## Monitoring Progress

### During Execution

Use progress bars to monitor:
```
Mapping:  75%|###               | 9/11 [00:29<00:10,  3.04s/stmt]
```

Meanings:
- `75%` — Percent complete
- `9/11` — 9 of 11 statements done
- `00:29` — Time elapsed
- `00:10` — Time remaining (estimate)
- `3.04s/stmt` — Speed

### In Another Terminal

Monitor database state:
```powershell
# Check row counts in real-time
while ($true) {
    docker exec epl_mysql mysql -u root -p1234 epl_dw -e "
    SELECT 
      'fact_match_events' as table_name,
      COUNT(*) as row_count
    FROM fact_match_events
    UNION ALL
    SELECT 'dim_team_mapping', COUNT(*) FROM dim_team_mapping
    UNION ALL
    SELECT 'dim_match_mapping', COUNT(*) FROM dim_match_mapping;
    "
    Start-Sleep -s 10
}
```

---

## Validation Queries

After loading completes, run these to verify:

### 1. Check Row Counts

```sql
SELECT 'fact_match' AS table_name, COUNT(*) AS row_count FROM fact_match
UNION ALL
SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
UNION ALL
SELECT 'dim_match_mapping', COUNT(*) FROM dim_match_mapping
UNION ALL
SELECT 'dim_team_mapping', COUNT(*) FROM dim_team_mapping;
```

**Expected output:**
```
table_name           row_count
─────────────────────────────
fact_match           830
fact_match_events    1362577
dim_match_mapping    684
dim_team_mapping     40
```

---

### 2. Check FK Integrity

```sql
-- Verify all fact_match events reference existing matches
SELECT COUNT(*) AS events_without_match
FROM fact_match_events fme
LEFT JOIN fact_match fm ON fme.match_id = fm.match_id
WHERE fm.match_id IS NULL;

-- Expected: 0 (all events have matching fact_match rows)
```

---

### 3. Check Team Mappings

```sql
-- Show all team mappings
SELECT * FROM dim_team_mapping ORDER BY statsbomb_team_id;

-- Show EPL teams (dim_team_id > 0)
SELECT COUNT(*) as epl_teams FROM dim_team_mapping 
WHERE dim_team_id > 0;
-- Expected: 17

-- Show international teams (mapped to -1)
SELECT COUNT(*) as international_teams FROM dim_team_mapping 
WHERE dim_team_id = -1;
-- Expected: 7
```

---

### 4. Check Match Distribution

```sql
-- Show events by match
SELECT TOP 10 
  fm.match_id,
  fm.home_team_id,
  fm.away_team_id,
  COUNT(*) as event_count
FROM fact_match_events fme
JOIN fact_match fm ON fme.match_id = fm.match_id
GROUP BY fm.match_id, fm.home_team_id, fm.away_team_id
ORDER BY event_count DESC;
```

**Sample output:**
```
match_id  home_team  away_team  event_count
────────────────────────────────────────────
380       1          2          4102
379       3          4          3987
...
```

---

## Performance Optimization

### Typical Breakdown

```
Mapping tables:      ~1 minute
fact_match:          <1 minute
Verification:        ~1 minute
fact_match_events:   ~5-8 minutes
Total:               ~7-11 minutes
```

### To Speed Up

1. **Increase Server Resources**
   - Allocate more CPU/RAM to MySQL container
   - Edit `docker-compose.yml`

2. **Batch Optimize**
   - Reduce index rebuilds
   - Run without constraint checks (not recommended)

3. **Parallel Load** (advanced)
   - Split event files into multiple batches
   - Load in parallel threads

---

## What Happens Inside

### Create Mapping Tables (Step 0)

```
1. Create dim_team_mapping via create_mapping_tables.sql
2. Create dim_match_mapping via create_mapping_tables.sql
3. Insert 40 team mappings (17 EPL + 7 international)
4. Insert 684 match pair mappings
```

### Load fact_match (Step 1)

```
1. Read from stg_e0_match_raw (830 rows)
2. Join with dim_team_mapping for team references
3. Insert into fact_match with all FK references
4. Verify 830 rows inserted
```

### Load fact_match_events (Steps 2-3)

```
1. Create temporary aggregation table (Step 1)
2. Verify mappings are correct (Step 2)
3. Join stg_events_raw with:
   - dim_match_mapping (event → match)
   - dim_team_mapping (team → team_id)
   - dim_player (player name → player_id)
4. Insert 1.36M events into fact_match_events
```

---

## Next Steps

After successful fact load:

1. **Run Analytics**
   ```sql
   -- Find top scorers
   SELECT TOP 10 player_name, COUNT(*) as shots
   FROM fact_match_events
   WHERE event_type = 'Shot'
   GROUP BY player_name
   ORDER BY shots DESC;
   ```

2. **Export Data**
   ```powershell
   # Export to CSV
   python -c "
   from src.etl.db import get_engine
   import pandas as pd
   
   engine = get_engine()
   df = pd.read_sql('SELECT * FROM fact_match_events LIMIT 1000', engine)
   df.to_csv('data/fact_match_events_sample.csv', index=False)
   "
   ```

3. **Monitor** ETL_Log table for execution history

---

## Common Questions

**Q: Why load mapping tables in step 0?**
A: Mappings are required to join fact data with dimensions. Must be created before loading facts.

**Q: Can I run --load-fact-tables without --full-etl?**
A: No, it requires staging and dimension tables to exist. Always run `--full-etl` first.

**Q: What if I only want to reload facts?**
A: Truncate fact tables, then run `--load-fact-tables` again (mappings will be updated).

**Q: How long does it take?**
A: ~7-11 minutes on typical hardware. Time varies with server specs and network latency.

**Q: Can I cancel mid-way?**
A: Yes, press Ctrl+C. The current SQL statement will complete, then rollback.

---

## Reference

- **Script Location:** `src/sql/` directory
- **Scripts Used:**
  - `create_mapping_tables.sql` (Step 0)
  - `load_fact_match.sql` (Step 1)
  - `load_fact_match_events_step1.sql` (Step 2)
  - `load_fact_match_events_step2.sql` (Step 3)
  - `load_fact_match_events_step3_final.sql` (Step 4)
  - `load_fact_match_events_step4_verify.sql` (Step 5)
  - `final_row_count.sql` (Step 6)

