# SQL Scripts Reference Guide# SQL Scripts Quick Reference



Quick reference for all SQL scripts used in the EPL DWH pipeline with descriptions and usage.This document provides a quick guide to the SQL scripts used in the EPL Data Warehouse ETL pipeline.



---## Production Scripts (Final & Optimized)



## 📋 Scripts Directory StructureLocated in: `src/sql/`



```### 1. **create_schema.sql**

src/sql/**Purpose:** Create all 21 database tables with proper structure  

├── create_schema.sql              # ⭐ Schema initialization**When to run:** During initial setup  

├── create_mapping_tables.sql      # Mapping tables**Execution time:** 1-2 seconds  

├── load_fact_match.sql            # Load match facts**What it creates:**

├── load_fact_match_events_step*.sql    # Event facts (multi-step)- 6 dimension tables (dim_date, dim_team, dim_player, etc.)

├── load_fact_player_stats.sql     # Player statistics- 3 fact tables (fact_match, fact_match_events, fact_player_stats)

└── final_row_count.sql            # Verification- 7 staging tables

```- 2 mapping tables (dim_match_mapping, dim_team_mapping)

- 3 ETL control tables

---- All indexes and foreign key constraints



## Core Scripts```bash

docker cp src/sql/create_schema.sql epl_mysql:/tmp/create_schema.sql

### 1. create_schema.sql (FOUNDATION)docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/create_schema.sql"

```

**Purpose:** Create complete database schema with 21 tables

**Result:** All 21 tables created with indexes and FK constraints ✓

**When to run:** 

- Initial setup---

- When resetting database

- Part of `--full-etl` pipeline### 2. **load_fact_match.sql**

**Purpose:** Load fact_match table with 830 CSV match records  

**Command:****When to run:** After dimensions are populated (fact_match depends on dim_team, dim_date, dim_referee, dim_stadium)  

```powershell**Execution time:** 2-3 seconds  

python -m src.etl.main --full-etl**What it does:**

```- Reads from `stg_e0_match_raw` (830 rows)

- Joins to dim_team, dim_date, dim_season, dim_referee, dim_stadium

Or manually:- Inserts complete match facts with all dimension keys

```bash

docker exec epl_mysql mysql -u root -p1234 epl_dw < src/sql/create_schema.sql```bash

```docker cp src/sql/load_fact_match.sql epl_mysql:/tmp/load_fact_match.sql

docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/load_fact_match.sql"

**Tables created:**```



**Dimensions (6 tables):****Result:** `fact_match` populated with 830 rows ✓

- `dim_date` — Calendar dates (1990-2025)

- `dim_team` — Team master data**Key Fields:**

- `dim_player` — Player master data- match_id (1-830, from CSV)

- `dim_referee` — Referee master data- home_team_id, away_team_id (from dim_team)

- `dim_stadium` — Stadium master data- date_key (from dim_date)

- `dim_season` — Season definitions- season_id (from dim_season)

- referee_id (from dim_referee)

**Facts (3 tables):**- stadium_id (from dim_stadium)

- `fact_match` — Match-level facts- Match result (home_score, away_score, result)

- `fact_match_events` — Event-level facts

- `fact_player_stats` — Player statistics per match---



**Staging (4 tables):**### 3. **load_fact_match_events_step1.sql** 

- `stg_events_raw` — Raw event data**Purpose:** Create temporary aggregation table to prepare for event loading  

- `stg_e0_match_raw` — Raw match data**Why needed:** Pre-aggregates 1.3M events into 760 rows to avoid timeout with correlated subqueries  

- `stg_player_raw` — Raw player data**Execution time:** ~30 seconds  

- `stg_team_raw` — Raw team data**What it does:**

- `stg_player_stats_fbref` — Raw player stats```sql

-- Collapses 1.3M rows → 760 (StatsBomb match, team) pairs

**Metadata/Mappings (5 tables):**CREATE TEMPORARY TABLE tmp_epl_team_per_match AS

- `etl_log` — ETL execution logSELECT  se.statsbomb_match_id,

- `etl_file_manifest` — File processing log        dtm.dim_team_id

- `etl_json_manifest` — JSON file processingFROM    stg_events_raw se

- `dim_match_mapping` — CSV ↔ StatsBomb match ID mappingJOIN    dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id

- `dim_team_mapping` — Team ID translationGROUP BY se.statsbomb_match_id, dtm.dim_team_id;



**Timing:** <5 secondsCREATE INDEX idx_tmp_match ON tmp_epl_team_per_match(statsbomb_match_id);

```

**Key constraints:**

- Foreign keys enforced```bash

- Primary keys on all dimension tablesdocker cp src/sql/load_fact_match_events_step1.sql epl_mysql:/tmp/step1.sql

- Surrogate keys for all dimensionsdocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step1.sql"

- Sentinel row (-1) for UNKNOWN values```



---**Result:** 

- tmp_epl_team_per_match created with 760 rows

### 2. create_mapping_tables.sql (DATA BRIDGE)- Index created for fast joins

- Ready for event loading

**Purpose:** Create mapping tables linking CSV to StatsBomb IDs

---

**When to run:** 

- After staging data loaded### 4. **load_fact_match_events_step2.sql**

- Before loading fact tables**Purpose:** Verify match mappings are complete before loading events  

- Part of `--load-fact-tables` command**When to run:** After Step 1, before Step 3  

**Execution time:** ~15 seconds  

**Command:****What it does:**

```powershell- Verifies `dim_match_mapping` has 684 valid match pairs

python -m src.etl.main --load-fact-tables- Confirms mapping coverage

```- No data modification (read-only validation)



Or manually:```bash

```bashdocker cp src/sql/load_fact_match_events_step2.sql epl_mysql:/tmp/step2.sql

docker exec epl_mysql mysql -u root -p1234 epl_dw < src/sql/create_mapping_tables.sqldocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step2.sql"

``````



**Tables populated:****Result:**

```

#### dim_team_mapping (40 rows)total_mappings: 684

unique_csv_matches: 342

Maps StatsBomb team IDs → dim_team surrogate keys:unique_statsbomb_matches: 190

```

| statsbomb_team_id | dim_team_id | Team Name |

|---|---|---|**What these numbers mean:**

| 1 | 1 | Arsenal |- 684: Total CSV↔StatsBomb match pairs available

| 22 | 2 | Aston Villa |- 342: Unique CSV matches (out of 830) that have StatsBomb events

| 23 | 3 | Chelsea |- 190: Unique StatsBomb matches mapped to CSV data

| ... | ... | ... |

| 30 | -1 | (International) |---

| 31 | -1 | (International) |

### 5. **load_fact_match_events_step3_final.sql** ✅ **MAIN EVENT LOADER**

**Split:****Purpose:** Load 1,362,577 match events into fact_match_events  

- 17 EPL teams (dim_team_id 1-23)**When to run:** After Steps 1-2 are complete  

- 7 international teams (dim_team_id = -1)**Execution time:** ~11 minutes  

- 2 sentinel rows for unmapped**CRITICAL for production use**



#### dim_match_mapping (684 rows)**What it does:**

```sql

Maps CSV match IDs → StatsBomb match UUIDs:INSERT INTO fact_match_events (match_id, event_type, player_id, team_id, minute, extra_time)

SELECT  dmm.csv_match_id,                    -- Match key

| csv_match_id | statsbomb_match_id | home_team | away_team |        se.type,                              -- Event type (Pass, Shot, etc.)

|---|---|---|---|        COALESCE(dp.player_id, 6808),         -- Player key (6808=UNKNOWN)

| 1 | 3242891 | Arsenal | Bournemouth |        COALESCE(dtm.dim_team_id, -1),        -- Team key (-1=UNKNOWN)

| 2 | 3242892 | Chelsea | Crystal Palace |        se.minute,

| ... | ... | ... | ... |        CASE WHEN se.statsbomb_period = 2 AND se.minute > 45 THEN se.minute - 45

             WHEN se.statsbomb_period >= 3 THEN se.minute

**Split:**             ELSE 0 END

- 380 EPL matchesFROM    stg_events_raw se

- 304 other matches (international friendlies, etc.)JOIN    dim_match_mapping dmm ON dmm.statsbomb_match_id = se.statsbomb_match_id

LEFT JOIN dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id

**Timing:** ~30-60 secondsLEFT JOIN dim_player dp ON dp.player_name = se.player_name

WHERE   se.status = 'LOADED'

**Key transformations:**  AND   se.minute BETWEEN 0 AND 120

```sql  AND   se.type IN ('Goal','Shot','Yellow Card','Red Card','Foul','Pass','Duel',

-- Team ID mapping via explicit VALUES list                    'Tackle','Interception','Clearance','Carry','Mistake');

INSERT INTO dim_team_mapping (statsbomb_team_id, dim_team_id)```

VALUES (1, 1), (22, 2), ...

```bash

-- Match ID mapping via joindocker cp src/sql/load_fact_match_events_step3_final.sql epl_mysql:/tmp/step3.sql

INSERT INTO dim_match_mappingdocker exec epl_mysql bash -c "time mysql -u root -p1234 epl_dw < /tmp/step3.sql"

SELECT sm.match_id, cm.match_id, ...```

FROM stg_statsbomb_matches sm

JOIN stg_csv_matches cm ON sm.home_team = cm.home_team AND sm.away_team = cm.away_team**Result:**

``````

total_events: 1,362,577 ✓

---matches_with_events: 342

players_seen: 286 + UNKNOWN

## Fact Loading Scriptsexecution_time: ~11 minutes

```

### 3. load_fact_match.sql (830 MATCHES)

**Key Design Features:**

**Purpose:** Load match-level facts from CSV data- Uses mapping tables (no correlated subqueries = no timeout)

- COALESCE to sentinel values for unmapped players/teams (preserves all events)

**When to run:** - Filters for high-quality event types

- After schema created and mappings populated- Normalizes StatsBomb periods to match minutes

- Part of `--load-fact-tables` (Step 1)- All FK constraints satisfied

- Run independently: `docker exec epl_mysql mysql -u root -p1234 epl_dw < src/sql/load_fact_match.sql`

---

**What it does:**

1. Reads from `stg_e0_match_raw` (830 matches)### 6. **load_fact_match_events_step4_verify.sql**

2. Joins with `dim_team_mapping` for team lookups**Purpose:** Verify events loaded correctly and show data quality metrics  

3. Joins with `dim_date` for date dimension**When to run:** After Step 3 completes  

4. Inserts into `fact_match` with all FK references**Execution time:** ~5 seconds  



**Output:****What it shows:**

``````sql

Inserted: 830 rows-- Overall statistics

Duplicates: 0SELECT COUNT(*) AS total_events,

Errors: 0       COUNT(DISTINCT match_id) AS matches_with_events,

```       COUNT(DISTINCT player_id) AS players_seen

FROM   fact_match_events;

**Table populated:** `fact_match` (830 rows)

-- Event type distribution

```sqlSELECT event_type, COUNT(*) FROM fact_match_events GROUP BY event_type ORDER BY COUNT(*) DESC;

CREATE TABLE fact_match (

  match_id INT PRIMARY KEY,-- Table row counts

  dim_match_id INT,SELECT 'fact_match' AS table_name, COUNT(*) FROM fact_match

  home_team_id INT,UNION ALL SELECT 'fact_match_events', COUNT(*) FROM fact_match_events

  away_team_id INT,UNION ALL SELECT 'dim_player', COUNT(*) FROM dim_player

  match_date DATE,UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team;

  home_goals INT,```

  away_goals INT,

  attendance INT,```bash

  venue VARCHAR(255),docker cp src/sql/load_fact_match_events_step4_verify.sql epl_mysql:/tmp/step4.sql

  referee VARCHAR(255),docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step4.sql"

  FOREIGN KEY (home_team_id) REFERENCES dim_team,```

  FOREIGN KEY (away_team_id) REFERENCES dim_team,

  FOREIGN KEY (match_date) REFERENCES dim_date**Result:**

);```

```Total Events: 1,362,577

Matches with Events: 342

**Timing:** <1 secondPlayers Seen: 286

Top Event Types:

**Sample row:**  Pass: 694,596 (51%)

```  Carry: 534,227 (39%)

match_id | home_team_id | away_team_id | match_date | home_goals | away_goals  Duel: 59,638

1        | 1 (Arsenal)  | 2 (Astn Villa) | 2023-01-14 | 2          | 0  Clearance: 38,739

```  Shot: 18,643

  ... 100+ more event types

---```



### 4. load_fact_match_events_step1.sql (CREATE STAGING)---



**Purpose:** Create temporary aggregation table for event loading### 7. **final_row_count.sql** & **count_rows.sql**

**Purpose:** Show final state of all 21 tables in the DWH  

**Part of:** `--load-fact-tables` (Step 2)**When to run:** Final verification after all loads complete  

**Execution time:** 2 seconds  

**What it does:**

1. Creates temporary table `tmp_events_with_ids````bash

2. Joins raw events with all required dimension IDsdocker cp src/sql/final_row_count.sql epl_mysql:/tmp/final.sql

3. Pre-calculates foreign keysdocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/final.sql"

4. Structures data for fact table insertion```



**Table created:** `tmp_events_with_ids` (temporary)**Result:** Complete row count for all 21 tables



```sql```

CREATE TEMPORARY TABLE tmp_events_with_ids ASTABLE_NAME                  ROW_COUNT

SELECT dim_date                    17,533

  se.event_id,dim_team                    31

  se.match_id,dim_player                  6,809

  se.event_type,fact_match                  830

  se.player_name,fact_match_events           1,362,577 ✓

  se.team_name,stg_events_raw              1,313,783

  fm.match_id as fact_match_id,          -- Join to fact_match...

  tm.dim_team_id,                        -- Join to dim_team via mapping```

  dp.player_id,                          -- Join to dim_player

  COALESCE(fdate.dim_date_id, -1) as date_id---

FROM stg_events_raw se

LEFT JOIN dim_match_mapping fm ON se.match_id = fm.statsbomb_match_id## Complete ETL Execution Sequence

LEFT JOIN dim_team_mapping tm ON se.team_id = tm.statsbomb_team_id

LEFT JOIN dim_player dp ON se.player_name = dp.player_name### Option A: Fresh Database Setup (Clean Start)

LEFT JOIN dim_date fdate ON DATE(se.event_timestamp) = fdate.date_value;

``````bash

# 1. Create schema and all tables

**Timing:** ~1-2 minutes (1.3M rows join)docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/create_schema.sql"



**Key benefit:** Pre-computes all joins once, then fact load is simpler# 2. (Staging tables are populated by Python ETL: src/etl/extract/)

python -m src.etl.main --staging

---

# 3. (Dimensions populated by Python ETL: src/etl/transform/)

### 5. load_fact_match_events_step2.sql (VERIFY MAPPINGS)python -m src.etl.main --warehouse



**Purpose:** Verify mapping table completeness before event load# 4. Load fact_match from CSV

docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/load_fact_match.sql"

**Part of:** `--load-fact-tables` (Step 3)

# 5. Load fact_match_events (4-step process)

**What it does:**docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step1.sql"  # ~30s

1. Count matches in mapping tabledocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step2.sql"  # ~15s

2. Verify each match has both CSV and StatsBomb IDsdocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step3.sql"  # ~11m

3. Check for null valuesdocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step4.sql"  # ~5s

4. Report verification results

# 6. Verify final state

**Sample query:**docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/final.sql"

```sql```

SELECT 

  'dim_match_mapping' as mapping_table,### Option B: Quick Verification (Database Already Populated)

  COUNT(*) as total_rows,

  COUNT(DISTINCT csv_match_id) as csv_ids,```bash

  COUNT(DISTINCT statsbomb_match_id) as statsbomb_ids,# Just run the verification scripts

  COUNT(CASE WHEN csv_match_id IS NULL THEN 1 END) as null_csv_ids,docker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/step4.sql"

  COUNT(CASE WHEN statsbomb_match_id IS NULL THEN 1 END) as null_sb_idsdocker exec epl_mysql bash -c "mysql -u root -p1234 epl_dw < /tmp/final.sql"

FROM dim_match_mapping;```

```

---

**Expected output:**

```## Troubleshooting

mapping_table    | total_rows | csv_ids | statsbomb_ids | null_csv_ids | null_sb_ids

─────────────────────────────────────────────────────────────────────────────────### "Cannot add or update a child row: Foreign key constraint fails"

dim_match_mapping | 684        | 684     | 684           | 0            | 0**Cause:** Player or team ID doesn't exist in dimension  

```**Solution:** Script already handles with COALESCE to sentinel values (player_id=6808, team_id=-1)



**Timing:** <1 second### "MySQL has gone away"

**Cause:** Query timeout on large JOIN operations  

**Purpose:** Ensures no missing mappings before loading 1.3M events**Solution:** Use the mapping table approach (Step 1-3) which avoids correlated subqueries



---### INFORMATION_SCHEMA shows 0 rows but SELECT COUNT(*) shows data

**Cause:** INFORMATION_SCHEMA not updated immediately after insert  

### 6. load_fact_match_events_step3_final.sql (LOAD EVENTS)**Solution:** Always use `SELECT COUNT(*)` for verification, not INFORMATION_SCHEMA



**Purpose:** Load all 1.3M+ match events into fact_match_events### Load time > 15 minutes

**Cause:** Missing indexes or correlated subqueries  

**Part of:** `--load-fact-tables` (Step 4)**Solution:** Ensure Step 1 index is created: `CREATE INDEX idx_tmp_match ON tmp_epl_team_per_match(statsbomb_match_id)`



**What it does:**---

1. Reads from `tmp_events_with_ids` (pre-joined data)

2. Maps to all required dimensions## Performance Notes

3. Applies business logic (e.g., sentinel values for UNKNOWN)

4. Inserts into `fact_match_events` with FK enforcement| Script | Time | Volume | Notes |

|--------|------|--------|-------|

**Table populated:** `fact_match_events` (1,362,577 rows)| create_schema.sql | 1-2s | 21 tables | Fast, creates structure |

| load_fact_match.sql | 2-3s | 830 rows | Small, reference load |

```sql| load_fact_match_events_step1.sql | 30s | 1.3M→760 rows | Aggregation reduces volume |

INSERT INTO fact_match_events (| load_fact_match_events_step2.sql | 15s | Validation | Read-only, quick |

  event_id,| load_fact_match_events_step3_final.sql | ~11m | 1.36M rows | Main load, optimized joins |

  match_id,| load_fact_match_events_step4_verify.sql | 5s | Validation | Read-only, verification |

  player_id,| final_row_count.sql | 2s | All 21 tables | Final check |

  team_id,

  event_type,**Total time for fresh load:** ~12-13 minutes (dominated by event load, which is excellent)

  event_timestamp,

  minute,---

  second,

  x_coordinate,## Key Takeaways

  y_coordinate,

  outcome✅ **Use the mapping table approach** (Step 1-3) instead of correlated subqueries  

)✅ **All scripts handle NULL/unmapped values** with sentinel records (UNKNOWN player, UNKNOWN team)  

SELECT ✅ **Foreign key constraints enabled throughout** for data quality assurance  

  e.event_id,✅ **Scripts are idempotent** where applicable (can re-run safely)  

  fm.match_id,✅ **All data is now loaded and verified** — the warehouse is production-ready

  COALESCE(dp.player_id, -1),  -- -1 for UNKNOWN player

  COALESCE(tm.dim_team_id, -1), -- -1 for unmapped team---

  e.event_type,

  e.event_timestamp,**Last Updated:** October 26, 2025  

  e.minute,**Status:** ✅ Production Ready

  e.second,
  e.x,
  e.y,
  e.outcome
FROM tmp_events_with_ids e
LEFT JOIN fact_match fm ON e.fact_match_id = fm.match_id
LEFT JOIN dim_player dp ON e.player_name = dp.player_name
LEFT JOIN dim_team_mapping tm ON e.team_id = tm.statsbomb_team_id;
```

**Timing:** ~5-8 minutes (1.3M row insert)

**Key features:**
- Uses temporary table for efficient joins
- Sentinel values (-1) for unmapped dimensions
- Foreign keys enforced (no orphaned records)
- Row-by-row verification

---

### 7. load_fact_match_events_step4_verify.sql (VALIDATION)

**Purpose:** Verify data integrity after event load

**Part of:** `--load-fact-tables` (Step 5)

**What it does:**
1. Check row counts
2. Verify foreign key relationships
3. Identify any orphaned records
4. Report data quality metrics

**Queries run:**
```sql
-- Count events by match
SELECT TOP 10 match_id, COUNT(*) as event_count
FROM fact_match_events
GROUP BY match_id
ORDER BY event_count DESC;

-- Verify all events reference existing matches
SELECT COUNT(*) as events_without_match
FROM fact_match_events fme
LEFT JOIN fact_match fm ON fme.match_id = fm.match_id
WHERE fm.match_id IS NULL;

-- Expected: 0 (no orphaned events)

-- Check event type distribution
SELECT event_type, COUNT(*) as count
FROM fact_match_events
GROUP BY event_type
ORDER BY count DESC;
```

**Expected output:**
```
match_id | event_count
─────────────────────
42       | 4102
15       | 3987
...
```

**Timing:** ~1-2 seconds (verification)

---

### 8. final_row_count.sql (SUMMARY)

**Purpose:** Show final row counts for all tables

**Part of:** `--load-fact-tables` (Step 6)

**What it does:**
1. Queries all major tables
2. Shows final row counts
3. Confirms pipeline success

**Query:**
```sql
SELECT 
  'dim_date' as table_name, COUNT(*) as row_count FROM dim_date
UNION ALL
SELECT 'dim_team', COUNT(*) FROM dim_team
UNION ALL
SELECT 'dim_player', COUNT(*) FROM dim_player
UNION ALL
SELECT 'fact_match', COUNT(*) FROM fact_match
UNION ALL
SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
UNION ALL
SELECT 'dim_match_mapping', COUNT(*) FROM dim_match_mapping
UNION ALL
SELECT 'dim_team_mapping', COUNT(*) FROM dim_team_mapping
ORDER BY table_name;
```

**Expected output:**
```
table_name           | row_count
─────────────────────────────────
dim_date             | 17533
dim_match_mapping    | 684
dim_player           | 6809
dim_referee          | 33
dim_season           | 7
dim_stadium          | 58
dim_team             | 31
dim_team_mapping     | 40
fact_match           | 830
fact_match_events    | 1362577
```

**Timing:** <1 second

---

## Optional Scripts

### 9. load_fact_player_stats.sql (OPTIONAL)

**Purpose:** Load player-level statistics (optional)

**When to run:** 
- After staging and dimensions loaded
- Run: `python -m src.etl.main --load-player-stats`

**What it does:**
1. Reads from `stg_player_stats_fbref`
2. Joins with dimensions
3. Loads into `fact_player_stats`

**Table populated:** `fact_player_stats`

**Timing:** ~2-5 minutes

**Currently:** 0 rows (optional feature)

---

## Execution Flow Diagram

```
create_schema.sql (1)
    ↓ (creates 21 tables)
    ├──→ create_mapping_tables.sql (2)
    │    ├──→ dim_team_mapping (40)
    │    └──→ dim_match_mapping (684)
    │
    ├──→ load_fact_match.sql (3)
    │    └──→ fact_match (830)
    │
    ├──→ load_fact_match_events_step1.sql (4)
    │    └──→ tmp_events_with_ids (pre-join)
    │
    ├──→ load_fact_match_events_step2.sql (5)
    │    └──→ Verify mappings (0 issues)
    │
    ├──→ load_fact_match_events_step3_final.sql (6)
    │    └──→ fact_match_events (1.36M)
    │
    ├──→ load_fact_match_events_step4_verify.sql (7)
    │    └──→ Verify FK integrity (0 orphans)
    │
    └──→ final_row_count.sql (8)
         └──→ Summary report
```

---

## Performance Notes

| Script | Duration | Rows | Throughput |
|--------|----------|------|------------|
| create_schema.sql | <5 sec | - | - |
| create_mapping_tables.sql | 30-60 sec | 724 | 12 rows/sec |
| load_fact_match.sql | <1 sec | 830 | 830 rows/sec |
| load_fact_match_events_step1.sql | 1-2 min | 1.3M | 650K rows/min |
| load_fact_match_events_step2.sql | <1 sec | - | - |
| load_fact_match_events_step3_final.sql | 5-8 min | 1.3M | 200K rows/min |
| load_fact_match_events_step4_verify.sql | 1-2 sec | - | - |
| final_row_count.sql | <1 sec | - | - |
| **Total** | **10-15 min** | **1.4M** | **140K rows/min** |

---

## Troubleshooting Scripts

### Check if schema exists

```sql
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'epl_dw';
```

### Clear all data (dangerous!)

```sql
-- Drop all fact tables
DROP TABLE IF EXISTS fact_match_events;
DROP TABLE IF EXISTS fact_player_stats;
DROP TABLE IF EXISTS fact_match;

-- Drop all mapping tables
DROP TABLE IF EXISTS dim_match_mapping;
DROP TABLE IF EXISTS dim_team_mapping;

-- Drop all staging tables
TRUNCATE TABLE stg_events_raw;
TRUNCATE TABLE stg_e0_match_raw;
TRUNCATE TABLE stg_player_raw;
TRUNCATE TABLE stg_team_raw;
TRUNCATE TABLE stg_player_stats_fbref;
```

### Verify data integrity

```sql
-- Check for orphaned facts
SELECT COUNT(*) FROM fact_match_events
WHERE match_id NOT IN (SELECT match_id FROM fact_match);

-- Check for duplicate events
SELECT event_id, COUNT(*) FROM fact_match_events
GROUP BY event_id
HAVING COUNT(*) > 1;

-- Check mapping coverage
SELECT 'Teams unmapped' as check_type, COUNT(*) as count
FROM dim_team_mapping WHERE dim_team_id IS NULL
UNION ALL
SELECT 'Matches unmapped', COUNT(*)
FROM dim_match_mapping WHERE csv_match_id IS NULL;
```

---

## Running Scripts Manually

### From SQL File

```bash
docker exec epl_mysql mysql -u root -p1234 epl_dw < src/sql/create_schema.sql
```

### From Command Line

```bash
docker exec epl_mysql mysql -u root -p1234 epl_dw -e "SELECT COUNT(*) FROM fact_match_events;"
```

### From Python

```python
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM fact_match_events"))
    print(f"Events: {result.scalar():,}")
```

---

## References

- **Full Pipeline Guide:** See `ETL_PIPELINE_GUIDE.md`
- **Fact Loading Details:** See `LOAD_FACT_TABLES_GUIDE.md`
- **Main Entry Point:** See `src/etl/main.py`

