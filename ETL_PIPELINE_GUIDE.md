# ETL Pipeline Guide - Complete Walkthrough# EPL Data Warehouse - ETL Pipeline Documentation



An in-depth guide to understanding and running the complete EPL Data Warehouse ETL pipeline.## Table of Contents



---1. [Overview](#overview)

2. [Architecture](#architecture)

## 📋 Table of Contents3. [ETL Step-by-Step Guide](#etl-step-by-step-guide)

4. [Final Data State](#final-data-state)

1. [Pipeline Overview](#pipeline-overview)5. [SQL Scripts Reference](#sql-scripts-reference)

2. [Command Reference](#command-reference)

3. [Step-by-Step Execution](#step-by-step-execution)---

4. [Data Transformations](#data-transformations)

5. [Troubleshooting](#troubleshooting)## Overview



---This document describes the **complete end-to-end ETL process** for the EPL Data Warehouse, including:

- Why each step is necessary

## Pipeline Overview- What data transformations occur

- How data flows through the warehouse

The ETL pipeline has **3 main stages**:- The final validated state



### Stage 1: **STAGING** (Extract & Load Raw Data)**Current Status:** ✅ **FULLY OPERATIONAL**

- Source: JSON, CSV, Excel files- **1,362,577 match events** loaded

- Target: `stg_*` tables (temporary raw data)- **342 matches** with complete event coverage  

- Purpose: Land all raw data without transformation- **All FK constraints satisfied**

- **Execution time:** ~11 minutes (efficient, no timeouts)

### Stage 2: **WAREHOUSE** (Transform & Dimension Load)

- Source: `stg_*` tables---

- Target: `dim_*` tables (cleaned dimensions)

- Purpose: Clean, deduplicate, standardize data## Architecture



### Stage 3: **FACT TABLES** (Load Business Facts)### Data Sources

- Source: `dim_*` + `stg_*` tables

- Target: `fact_*` tables (analysis-ready data)| Source | Type | Volume | Purpose |

- Purpose: Create business-level fact tables with FK constraints|--------|------|--------|---------|

| **StatsBomb Open Data** | JSON event files | 1.3M+ events | Detailed match events (passes, shots, fouls, etc.) |

---| **CSV Match Data** | Flat files | 830 matches | EPL match metadata (teams, dates, venues, referees) |

| **Dimension Files** | YAML/JSON | ~7K rows total | Teams, players, referees, seasons, stadiums |

## Command Reference

### Database Schema

### 1. Test Database Connection

```

```powershell21 Tables organized as:

python -m src.etl.main --test-db

```DIMENSIONS (6)

├── dim_date (17,533 rows)

**What it does:**├── dim_team (31 rows - 1 UNKNOWN)

- Verifies MySQL connection├── dim_season (7 rows)

- Shows database version├── dim_player (6,809 rows - incl. UNKNOWN)

- Confirms schema is accessible├── dim_referee (33 rows)

└── dim_stadium (58 rows)

**Output example:**

```FACTS (3)

DB connectivity test result:├── fact_match (830 rows - CSV data)

SELECT 1 -> 1├── fact_match_events (1,362,577 rows - StatsBomb events) ✅

VERSION -> 8.0.32-0ubuntu0.22.04.1└── fact_player_stats (0 rows - optional)

```

STAGING (7)

---├── stg_events_raw (1,313,783 rows)

├── stg_e0_match_raw (830 rows)

### 2. Load Staging Only (Extract)├── stg_team_raw (60 rows)

├── stg_player_raw (23,926 rows)

```powershell├── stg_player_stats_fbref (0 rows)

python -m src.etl.main --staging└── stg_referee_raw (32 rows)

```

MAPPINGS (2)

**What it does:**├── dim_match_mapping (684 CSV↔StatsBomb match pairs)

1. Reads from `data/raw/` sources (CSV, JSON, Excel)└── dim_team_mapping (40 StatsBomb↔EPL team mappings)

2. Loads raw data into staging tables

3. Creates audit trail in manifest tablesETL CONTROL (3)

4. No transformations applied├── ETL_Log (7 entries)

├── ETL_File_Manifest (3 entries)

**Staging tables created:**├── ETL_Api_Manifest (3 entries)

- `stg_events_raw` — Raw event data└── ETL_JSON_Manifest (666 entries)

- `stg_e0_match_raw` — Raw match data```

- `stg_player_raw` — Raw player data

- `stg_team_raw` — Raw team data---

- `stg_player_stats_fbref` — Raw player stats

## ETL Step-by-Step Guide

**Timing:** ~5-10 minutes

### **PHASE 1: Schema Setup**

---

#### **Step 1.1: Create Database Schema**

### 3. Load Warehouse Only (Transform)

**Script:** `src/sql/create_schema.sql`

```powershell

python -m src.etl.main --warehouse**Why:**

```- Defines all 21 tables with proper data types

- Establishes primary keys and unique constraints

**What it does:**- Creates foreign key relationships for referential integrity

1. Reads from staging tables- Creates indexes for query performance

2. Cleans & standardizes data

3. Removes duplicates & nulls**What it does:**

4. Creates dimension tables with surrogate keys```sql

-- Creates all tables with:

**Dimension tables created:**-- ✓ Proper column definitions

- `dim_date` (17,533 rows)-- ✓ Primary key constraints

- `dim_team` (31 rows)-- ✓ Unique constraints (e.g., unique season/team combinations)

- `dim_player` (6,809 rows)-- ✓ Foreign key constraints (e.g., fact_match_events → dim_player)

- `dim_referee` (33 rows)-- ✓ Indexes on high-cardinality columns

- `dim_stadium` (58 rows)-- ✓ Timestamps for audit trails

- `dim_season` (7 rows)```



**Timing:** ~2-3 minutes**Execution:**

```bash

---docker cp src/sql/create_schema.sql epl_mysql:/tmp/create_schema.sql

docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/create_schema.sql"

### 4. Full ETL (Staging + Warehouse)```



```powershell**Validates:**

python -m src.etl.main --full-etl- All 21 tables created ✓

```- All indexes built ✓

- FK constraints in place ✓

**What it does:**

1. Runs staging (Stage 1)---

2. Runs warehouse (Stage 2)

3. Creates both raw and conformed data### **PHASE 2: Data Staging**



**Total timing:** ~10-15 minutes#### **Step 2.1: Load StatsBomb Events into Staging**



**Recommended workflow:****Executed by:** `src/etl/extract/statsbomb_reader.py`

- Use this for initial data load

- Sets up all prerequisites for fact tables**Why:**

- Decouples data extraction from transformation

---- Allows inspection and validation of raw data

- Provides audit trail of loaded events

### 5. Load Fact Tables- Enables re-processing without re-downloading



```powershell**What it does:**

python -m src.etl.main --load-fact-tables- Filters 3,464 StatsBomb event files → 380 EPL-only files

```- Extracts match metadata and 1.3M+ events

- Inserts into `stg_events_raw` with columns:

**What it does:**  - `statsbomb_match_id`, `team_id`, `player_id`, `player_name`

1. Populates mapping tables (dim_team_mapping, dim_match_mapping)  - `type` (event type: Pass, Shot, Duel, etc.)

2. Loads fact_match (830 matches from CSV)  - `minute`, `statsbomb_period`

3. Loads fact_match_events (1.36M events from staging)  - `status` = 'LOADED' for filtering

4. Verifies data integrity with FK checks

**Result:** `stg_events_raw` populated with **1,313,783 rows**

**Facts loaded:**

- `fact_match` — 830 rows#### **Step 2.2: Load CSV Match Data into Staging**

- `fact_match_events` — 1,362,577 rows

- `dim_match_mapping` — 684 rows**Executed by:** `src/etl/extract/csv_loader.py`

- `dim_team_mapping` — 40 rows

**Why:**

**Total timing:** ~7-11 minutes- CSV provides match-level metadata (teams, dates, venues, referees)

- StatsBomb events need to be joined to CSV matches for proper ID mapping

**Prerequisites:**- Staging allows validation before loading into fact tables

- Must run `--full-etl` first

- Requires staging and dimensions to exist**What it does:**

- Reads EPL season CSVs (E0 format: home team, away team, score, etc.)

---- Inserts into `stg_e0_match_raw`:

  - `match_id`, `home_team`, `away_team`, `date`, `venue`, `referee`

### 6. Load Player Stats  - Match results and league position data



```powershell**Result:** `stg_e0_match_raw` populated with **830 rows**

python -m src.etl.main --load-player-stats

```#### **Step 2.3: Load Dimension Data into Staging**



**What it does:****Executed by:** Python ETL modules (`src/etl/transform/`)

1. Reads from `stg_player_stats_fbref` (staging)

2. Transforms player-level statistics**Why:**

3. Loads into `fact_player_stats`- Dimension data comes from multiple sources (StatsBomb, CSV, static data)

- Staging allows combining and deduplicating from different sources

**Timing:** ~2-5 minutes- Enables validation and cleaning before loading into dimensions



**Prerequisites:****What it does:**

- Requires player stats to be staged first- `stg_team_raw`: Teams from StatsBomb + CSV (60 rows)

- Optional (not part of main ETL)- `stg_player_raw`: Players from StatsBomb event data (23,926 rows)

- `stg_referee_raw`: Referees from CSV (32 rows)

---

---

### 7. Complete Player Pipeline (All-in-One)

### **PHASE 3: Dimension Population**

```powershell

python -m src.etl.main --complete-player-pipeline#### **Step 3.1-3.6: Load Dimension Tables**

```

**Executed by:** Python ETL modules

**What it does (6 steps):**

1. Recreate schema with all seasons (2017-2026)**Why:**

2. Run full ETL pipeline- Dimensions must be loaded FIRST before facts (FK constraint order)

3. Generate mock FBRef player stats- Deduplication and normalization needed (e.g., "Arsenal" → "Arsenal FC")

4. Stage player stats CSVs- Surrogate keys (dim_team_id, dim_player_id) required for joins

5. Load player statistics

6. Populate mapping tables**Dimensions loaded:**



**Total timing:** ~20-30 minutes1. **`dim_date`** (17,533 rows)

   - Why: Every match and event needs a date key

**Use case:** Complete initialization from scratch   - Contains: All dates from 1990-2025



---2. **`dim_season`** (7 rows)

   - Why: Group matches and events by EPL season

## Step-by-Step Execution   - Contains: 2018-2019 through 2024-2025



### Scenario A: First-Time Setup3. **`dim_team`** (31 rows - 20 EPL + UNKNOWN)

   - Why: Core dimension; every match involves 2 teams

```powershell   - Mapping: StatsBomb team names → CSV team names

# Step 1: Start database   - Special: 1 UNKNOWN team for unmapped events

docker-compose up -d

4. **`dim_referee`** (33 rows)

# Step 2: Activate Python environment   - Why: Fact matches reference referee data

.\.venv\Scripts\Activate.ps1   - Contains: Referee names from CSV matches



# Step 3: Test connection5. **`dim_stadium`** (58 rows)

python -m src.etl.main --test-db   - Why: Fact matches reference venue/stadium

   - Contains: EPL stadium names and capacity

# Step 4: Run complete ETL (30-45 minutes)

python -m src.etl.main --full-etl6. **`dim_player`** (6,809 rows - incl. UNKNOWN)

   - Why: Events reference players; need name normalization

# Step 5: Load fact tables (7-11 minutes)   - Mapping: StatsBomb player names matched to dimension players

python -m src.etl.main --load-fact-tables   - Special: 1 UNKNOWN player (player_id=6808) for unmapped events

```

---

**Total time:** ~45-60 minutes

### **PHASE 4: Mapping Tables (CRITICAL)**

---

#### **Step 4.1: Create Match Mapping Table**

### Scenario B: Incremental Updates

**Script:** Part of `create_schema.sql`; populated by ETL logic

```powershell

# Only re-load new data (skip schema recreation)**Table:** `dim_match_mapping`

python -m src.etl.main --staging

**Why:** 

# Transform updated staging data- **CRITICAL PROBLEM:** StatsBomb match IDs ≠ CSV match IDs

python -m src.etl.main --warehouse  - StatsBomb: 3,753,972 - 3,754,351 (internal IDs)

  - CSV: 1 - 830 (row numbers)

# Load updated facts- Solution: Create lookup table matching them by logic (team pair + date)

python -m src.etl.main --load-fact-tables

```**What it contains:**

```

**Total time:** ~20-30 minutescsv_match_id (1-830)  ←→  statsbomb_match_id (3.7M+)

```

---

**Population logic:**

### Scenario C: Facts Only (Already Staged)- Group StatsBomb events by match

- Identify home/away team pair + approximate date

```powershell- Match to CSV row with same team pair and date

# If staging and dimensions already exist- Result: **684 valid mappings** (81% coverage)

python -m src.etl.main --load-fact-tables

```**Result:** `dim_match_mapping` with **684 rows**



**Total time:** ~7-11 minutes**Why 684 and not 830?**

- Some StatsBomb matches have incomplete/duplicate data

---- Some CSV matches don't have corresponding StatsBomb data

- 684 mappings represent the high-quality intersection

## Data Transformations

#### **Step 4.2: Create Team Mapping Table**

### Team Name Standardization

**Script:** Part of `create_schema.sql`; populated during dimension loading

**Problem:** Raw data has team name variations

- CSV: "Man City", "Man. City", "Manchester City"**Table:** `dim_team_mapping`

- StatsBomb: "Manchester City"

**Why:**

**Solution:** Conformation logic in SQL- StatsBomb uses internal team IDs different from our `dim_team_id`

```sql- Events reference StatsBomb team IDs; facts need `dim_team_id`

CASE- Solution: Create lookup mapping both

  WHEN team_name LIKE '%Man City%' THEN 'Manchester City'

  WHEN team_name LIKE '%Man Utd%' THEN 'Manchester United'**What it contains:**

  ...```

ENDstatsbomb_team_id  ←→  dim_team_id

```(StatsBomb internal)    (our EPL dimension)

```

**Result:** All teams mapped to canonical names

**Result:** `dim_team_mapping` with **40 entries**

---

---

### Player Name Deduplication

### **PHASE 5: Fact Table Loading (Main Data Load)**

**Problem:** Same player appears with multiple name variations

- "Mohamed Salah", "M. Salah", "Salah"#### **Step 5.1: Load Fact Match Table**



**Solution:** **Script:** `src/sql/load_fact_match.sql`

1. Extract from event data (StatsBomb provides clean names)

2. Group by standardized name**Why:**

3. Create single `dim_player` entry per unique player- Fact tables depend on all dimensions being populated first

- CSV matches provide business key data (teams, dates, scores)

**Result:** 6,809 unique players- Creates the 830 match facts that events will link to



---**What it does:**

```sql

### Match ID MappingINSERT INTO fact_match (match_id, home_team_id, away_team_id, ...)

SELECT 

**Problem:** CSV and StatsBomb use different match IDs    stg.match_id,

- CSV: `match_id` (1-830)    dt_home.team_id AS home_team_id,

- StatsBomb: Different UUID system    dt_away.team_id AS away_team_id,

    ...

**Solution:** Create `dim_match_mapping` tableFROM stg_e0_match_raw stg

```LEFT JOIN dim_team dt_home ON stg.home_team = dt_home.team_name

┌──────────────────────┬──────────────────────┐LEFT JOIN dim_team dt_away ON stg.away_team = dt_away.team_name

│ csv_match_id         │ statsbomb_match_id   │LEFT JOIN dim_date dd ON stg.date = dd.date_key

├──────────────────────┼──────────────────────┤LEFT JOIN dim_season ds ON YEAR(stg.date) = ds.season_year

│ 1 (Arsenal vs Bournem) │ 3242891 (SB UUID)  │LEFT JOIN dim_referee dr ON stg.referee = dr.referee_name

│ 2 (Chelsea vs Palace)  │ 3242892 (SB UUID)  │LEFT JOIN dim_stadium dst ON stg.venue = dst.stadium_name

└──────────────────────┴──────────────────────┘WHERE stg.match_id BETWEEN 1 AND 830;

``````



**Result:** 684 match pairs matched**Result:** `fact_match` with **830 rows** ✓



------



### Team ID Translation#### **Step 5.2-5.4: Load Fact Match Events (3-Step Optimized Process)**



**Problem:** StatsBomb team IDs ≠ dim_team surrogate keys**Problem being solved:**

- StatsBomb ID 1 = Arsenal- 1.3M events need to join to 830 matches

- But dim_team_id might be different- Direct correlated subqueries = **MySQL timeout** (>180 seconds)

- Need pre-aggregation strategy

**Solution:** Create `dim_team_mapping` table

```##### **Step 5.2a: Create Temporary Aggregation Table**

┌─────────────────────┬─────────────────┐

│ statsbomb_team_id   │ dim_team_id     │**Script:** `load_fact_match_events_step1.sql`

├─────────────────────┼─────────────────┤

│ 1                   │ 1 (Arsenal)     │**Why:**

│ 22                  │ 2 (Aston Villa) │- Pre-aggregates 1.3M rows into 760 (statsbomb_match_id, team_id) pairs

│ 30 (International)  │ -1 (UNKNOWN)    │- Avoids row-by-row processing with correlated subqueries

└─────────────────────┴─────────────────┘- Reduces memory and CPU usage

```

**What it does:**

**Result:** 40 team mappings (17 EPL + 7 international → -1)```sql

CREATE TEMPORARY TABLE tmp_epl_team_per_match AS

---SELECT  se.statsbomb_match_id,

        dtm.dim_team_id

## TroubleshootingFROM    stg_events_raw se

JOIN    dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id

### Issue: Database Connection FailedGROUP BY se.statsbomb_match_id, dtm.dim_team_id;

```

**Error:**

```**Result:** 760 aggregated rows for fast joins ✓

DB connectivity test failed: (2003, "Can't connect to MySQL server")

```##### **Step 5.2b: Verify Mapping Coverage**



**Solution:****Script:** `load_fact_match_events_step2.sql`

```powershell

# Ensure Docker container is running**Why:**

docker ps | findstr epl_mysql- Ensures mappings are complete before loading events

- Validates that match pairs are correct

# If not running, start it

docker-compose up -d**Result:** 684 valid mappings ✓



# Wait 10 seconds for MySQL to initialize##### **Step 5.2c: Load Events with Optimized Join Logic**

Start-Sleep -s 10

**Script:** `load_fact_match_events_step3_final.sql` ✅ **MAIN LOADER**

# Test again

python -m src.etl.main --test-db**Why:**

```- Uses mapping tables instead of correlated subqueries

- Handles NULL player/team values gracefully (→ UNKNOWN sentinel values)

---- Filters for quality events only (specific event types, valid minutes)



### Issue: "Table Already Exists" Error**What it does:**

```sql

**Error:**INSERT INTO fact_match_events (

```    match_id, event_type, player_id, team_id, minute, extra_time

1050 (42S01): Table 'dim_team' already exists)

```SELECT  dmm.csv_match_id,                    -- Match key (CSV ID)

        se.type,                              -- Event type (Pass, Shot, etc.)

**Solution:**        COALESCE(dp.player_id, 6808),         -- Player key (6808=UNKNOWN)

```powershell        COALESCE(dtm.dim_team_id, -1),        -- Team key (-1=UNKNOWN)

# Option 1: Clear and restart        se.minute,                            -- Event minute

docker-compose down -v        CASE WHEN se.statsbomb_period = 2 AND se.minute > 45 THEN se.minute - 45

docker-compose up -d             WHEN se.statsbomb_period >= 3 THEN se.minute

             ELSE 0 END                       -- Extra time calculation

# Option 2: Drop tables manuallyFROM    stg_events_raw se

docker exec epl_mysql mysql -u root -p1234 epl_dw -e "JOIN    dim_match_mapping dmm 

DROP TABLE IF EXISTS fact_match_events;        ON dmm.statsbomb_match_id = se.statsbomb_match_id  -- Match lookup

DROP TABLE IF EXISTS fact_match;LEFT JOIN dim_team_mapping dtm 

DROP TABLE IF EXISTS dim_team;        ON dtm.statsbomb_team_id = se.team_id              -- Team lookup

"LEFT JOIN dim_player dp 

        ON dp.player_name = se.player_name                 -- Player lookup

# Then rerun pipelineWHERE   se.status = 'LOADED'                  -- Filter for valid records

python -m src.etl.main --full-etl  AND   se.minute BETWEEN 0 AND 120           -- Ignore extra events

```  AND   se.type IN (                          -- Filter quality event types

        'Goal','Shot','Yellow Card','Red Card',

---        'Foul','Pass','Duel','Tackle',

        'Interception','Clearance','Carry','Mistake');

### Issue: Out of Memory or Timeouts```



**Error:****Key Design Decisions:**

```

Lost connection to MySQL server during query| Decision | Reason |

```|----------|--------|

| **LEFT JOIN dim_player** | Some events have NULL player (own goals, set pieces) |

**Solution:**| **COALESCE(dp.player_id, 6808)** | Map NULLs to UNKNOWN player (preserves record) |

1. Reduce chunk size in Python code (250 → 100)| **COALESCE(dtm.dim_team_id, -1)** | Map unknown teams to -1 sentinel |

2. Run staging only, then warehouse separately| **WHERE se.minute BETWEEN 0 AND 120** | Exclude invalid/duplicate events |

3. Clear old data: `TRUNCATE TABLE stg_events_raw;`| **Event type filter** | Include meaningful events; exclude metadata events |

| **Extra time calculation** | Normalize StatsBomb periods to match minutes |

---

**Result:** `fact_match_events` with **1,362,577 rows** ✅

### Issue: Foreign Key Constraints Violated

---

**Error:**

```#### **Step 5.3: Verify Loaded Data**

1452 (23000): Cannot add or update child row

```**Script:** `load_fact_match_events_step4_verify.sql`



**Meaning:** Fact table references non-existent dimension**Why:**

- Confirms all data loaded correctly

**Solution:**- Shows event distribution and data quality

1. Verify dimensions were created: Check `dim_team`, `dim_player`

2. Rerun warehouse step: `python -m src.etl.main --warehouse`**Result:**

3. Check for missing sentinel row (`-1` for UNKNOWN)```

Total Events: 1,362,577

---Matches with Events: 342

Players Seen: 286 + UNKNOWN

## Performance NotesTeams Involved: 15 (20 EPL teams, some seasonal)

Event Distribution:

### Typical Execution Times  - Pass: 694,596 (51%)

  - Carry: 534,227 (39%)

| Step | Duration | Rows | Throughput |  - Duel: 59,638

|------|----------|------|------------|  - Clearance: 38,739

| Staging | 5-10 min | 1.3M events | 130K rows/min |  - Shot: 18,643

| Warehouse (Dimensions) | 2-3 min | 25K rows | 10K rows/min |  - Interception: 16,734

| Populate Mappings | 1 min | 724 rows | 724 rows/min |  - Other: ~100 types

| Load fact_match | <1 min | 830 rows | 830 rows/min |```

| Load fact_match_events | 5-8 min | 1.36M events | 200K rows/min |

| **Total** | **15-25 min** | **1.4M rows** | **60K rows/min** |---



---## Final Data State



### Optimization Techniques### **Row Counts by Category**



1. **Per-File Transactions**#### **Dimensions (All Populated)**

   - Each JSON file loaded in separate transaction```

   - Prevents long-lived connectionsdim_date:              17,533 rows ✓

   - Allows partial recoverydim_team:              31 rows (20 EPL + UNKNOWN) ✓

dim_season:            7 rows ✓

2. **Chunked Inserts**dim_player:            6,809 rows (6,808 + UNKNOWN) ✓

   - Default chunksize: 250 rowsdim_referee:           33 rows ✓

   - Balances memory vs. round-tripsdim_stadium:           58 rows ✓

   - Can be tuned based on system resources```



3. **Index Strategy**#### **Facts (Target Tables)**

   - Dimensions indexed on business keys```

   - Facts indexed on foreign keysfact_match:            830 rows ✓ (All CSV matches)

   - Fact table clustered on match_idfact_match_events:     1,362,577 rows ✓ (All mapped events)

fact_player_stats:     0 rows (Optional, not needed)

---```



## Next Steps#### **Staging (Source Data)**

```

After successful pipeline execution:stg_events_raw:        1,313,783 rows (StatsBomb events)

stg_e0_match_raw:      830 rows (CSV matches)

1. **Verify Data:**stg_team_raw:          60 rows (Team dimension source)

   ```sqlstg_player_raw:        23,926 rows (Player dimension source)

   SELECT COUNT(*) FROM fact_match_events;stg_referee_raw:       32 rows (Referee dimension source)

   SELECT COUNT(DISTINCT match_id) FROM fact_match;stg_player_stats_fbref: 0 rows (Not loaded)

   SELECT COUNT(DISTINCT player_id) FROM dim_player;```

   ```

#### **Mappings (Lookup Tables)**

2. **Run Analytics:**```

   ```sqldim_match_mapping:     684 rows (CSV ↔ StatsBomb matches)

   SELECT player_name, COUNT(*) as eventsdim_team_mapping:      40 rows (StatsBomb ↔ EPL teams)

   FROM fact_match_events```

   GROUP BY player_name

   ORDER BY events DESC#### **ETL Control (Audit Trail)**

   LIMIT 10;```

   ```ETL_Log:               7 entries (Load history)

ETL_File_Manifest:     3 entries (File tracking)

3. **Monitor Performance:**ETL_Api_Manifest:      3 entries (API calls)

   - Check `ETL_Log` table for execution timesETL_JSON_Manifest:     666 entries (JSON files processed)

   - Review error messages in `ETL_Log````

   - Identify slow steps for optimization

---

---

## SQL Scripts Reference

## References

### **Production Scripts (Final & Clean)**

- **Database Schema:** See `src/sql/create_schema.sql`

- **SQL Scripts:** See `src/sql/` directory| Script | Purpose | Volume | Time |

- **Source Code:** See `src/etl/main.py`|--------|---------|--------|------|

- **Configuration:** See `src/etl/config.py`| `create_schema.sql` | Database schema setup | N/A | 1-2s |

| `load_fact_match.sql` | Load 830 CSV matches | 830 rows | 2-3s |

| `load_fact_match_events_step1.sql` | Create temp aggregation | 1.3M → 760 rows | 30s |
| `load_fact_match_events_step2.sql` | Verify mappings | 684 mappings | 15s |
| `load_fact_match_events_step3_final.sql` | **Load 1.3M events** | **1,362,577 rows** | **~11 min** |
| `load_fact_match_events_step4_verify.sql` | Verify loaded data | Validation query | 5s |
| `final_row_count.sql` | Show final DWH state | All 21 tables | 2s |

### **Location**
```
src/sql/
├── create_schema.sql
├── load_fact_match.sql
├── load_fact_match_events_step1.sql
├── load_fact_match_events_step2.sql
├── load_fact_match_events_step3_final.sql
├── load_fact_match_events_step4_verify.sql
├── final_row_count.sql
└── count_rows.sql
```

---

## Execution Flow Summary

```
PHASE 1: SCHEMA SETUP
└─ create_schema.sql
   └─ Creates 21 tables, indexes, FK constraints

PHASE 2: DATA STAGING
├─ StatsBomb extraction → stg_events_raw (1.3M rows)
├─ CSV loading → stg_e0_match_raw (830 rows)
└─ Dimension staging → stg_*_raw tables

PHASE 3: DIMENSION POPULATION
├─ dim_date (17,533 rows)
├─ dim_season (7 rows)
├─ dim_team (31 rows) + dim_team_mapping (40 rows)
├─ dim_player (6,809 rows)
├─ dim_referee (33 rows)
└─ dim_stadium (58 rows)

PHASE 4: MAPPING TABLES
├─ dim_match_mapping (684 CSV ↔ StatsBomb pairs)
└─ dim_team_mapping (40 team ID translations)

PHASE 5: FACT LOADING
├─ load_fact_match.sql → fact_match (830 rows) ✓
└─ load_fact_match_events (3-step process)
   ├─ Step 1: Create temp aggregation
   ├─ Step 2: Verify mappings
   └─ Step 3: Load 1,362,577 events ✓

PHASE 6: VERIFICATION
└─ Confirm all 21 tables populated correctly
```

---

## Performance Notes

- **Total load time:** ~11 minutes (dominated by event insertion, which is excellent for 1.3M rows)
- **Peak memory:** ~2GB (MySQL container)
- **Concurrency:** Single-threaded (safe for production)
- **Indexing:** All indexes built before data load (optimal for inserts)
- **FK constraints:** Enabled throughout (catches data quality issues)

---

## Key Design Decisions

1. **Staging → Dimension → Fact order**
   - Enforces data quality and FK constraint satisfaction
   - Allows incremental reloading without affecting dimensions

2. **Mapping tables instead of correlated subqueries**
   - Correlated subqueries timeout on 1.3M rows
   - Mapping tables enable efficient joins

3. **Sentinel values for unknown dimensions**
   - UNKNOWN player (ID=6808) for missing player names
   - UNKNOWN team (ID=-1) for unmapped teams
   - Preserves all events while maintaining referential integrity

4. **Event type filtering**
   - Excludes metadata events (Half Start, Half End, etc.)
   - Includes only analytically relevant events
   - Result: ~1.3M meaningful events from ~1.4M total

5. **Minute validation (0-120)**
   - Filters out duplicate/erroneous events
   - Extra time calculation normalizes StatsBomb periods

---

## Troubleshooting

### Issue: `fact_match_events` loads but INFORMATION_SCHEMA shows 0 rows

**Reason:** INFORMATION_SCHEMA not immediately updated  
**Solution:** Use direct COUNT(*) to verify: `SELECT COUNT(*) FROM fact_match_events;`

### Issue: FK constraint violation during load

**Reason:** Player or team ID doesn't exist in dimension  
**Solution:** Use COALESCE to sentinel value (6808 for player, -1 for team)

### Issue: Load takes >15 minutes

**Reason:** Correlated subqueries or missing indexes  
**Solution:** Use mapping tables approach (step1/2/3) instead of direct joins

---

## Next Steps

1. **Aggregate queries:** Run analytical queries on fact_match_events
2. **Player stats load:** Populate fact_player_stats if needed
3. **Incremental loads:** Set up Delta loading for new StatsBomb data
4. **Performance tuning:** Add partitioning for 1.3M row table

---

**Document Version:** 1.0  
**Last Updated:** October 26, 2025  
**Status:** ✅ Production Ready
