# MEMBER 4: Facts & Mappings Deliverables Guide 🔴 HARD

**Project:** English Premier League Data Warehouse  
**Member:** Member 4 - Facts, Mappings & Aggregations  
**Difficulty Level:** 🔴 HARD (Complex logic, 1.3M scale, deduplication)  
**Estimated Time:** 3-5 days  
**Viva Slot:** 8 minutes (strict timing)

---

## 📋 Quick Overview

You are responsible for **loading the 3 fact tables** (where most of the data lives) and creating **mapping tables** to connect different ID systems across data sources. Your work is complex because you're handling **1.3M+ events** at scale with **multi-step loading logic** and **deduplication guarantees**.

```
WHAT YOU RECEIVE FROM PREVIOUS MEMBERS:
├─ From Member 1: Staging tables with 1.3M+ raw events & 830 matches
├─ From Member 2: Schema with 21 tables ready for data
└─ From Member 3: 6 conformed dimensions (teams, players, referees, dates, stadiums, seasons)

WHAT YOU DELIVER:
├─ 3 fact tables fully loaded (match, events, player stats)
├─ 2 mapping tables (team mapping, match mapping)
├─ Deduplication system (ETL_Events_Manifest prevents duplicate events)
├─ Aggregation logic (1.3M events correctly mapped to 830 matches)
└─ Full referential integrity (all FKs valid, zero violations)

SUCCESS METRIC:
✅ 1.3M+ events loaded without a single duplicate
✅ 830 matches loaded with correct event counts
✅ All dimensions referenced (zero orphaned records)
✅ Run twice without duplicates (idempotent loading)
```

---

## 🎯 Your 3 Main Deliverables

### **DELIVERABLE 1: Mapping Tables** 📍

**Purpose:** Connect IDs from different data sources (StatsBomb uses different IDs than FootballData.org)

#### **A. dim_team_mapping** (Team ID Translation)

| StatsBomb Team ID | DWH dim_team_id | Team Name | Source |
|------------------|-----------------|-----------|--------|
| 217 | 1 | Manchester United | Both sources |
| 218 | 2 | Manchester City | Both sources |
| 219 | 3 | Liverpool | Both sources |
| ... | ... | ... | ... |

**What you need to do:**
- Read teams from staging (stg_team_raw)
- Match StatsBomb team_id to DWH team_id
- Create INSERT script: `create_mapping_tables.sql`
- Result: ~40 team mappings

**Example SQL:**
```sql
INSERT INTO dim_team_mapping (statsbomb_team_id, dwh_team_id, team_name, mapping_date)
SELECT DISTINCT 
    stg.statsbomb_team_id,
    dt.team_id,
    stg.team_name,
    CURDATE()
FROM stg_team_raw stg
JOIN dim_team dt ON stg.team_name = dt.team_name
WHERE stg.statsbomb_team_id IS NOT NULL;
```

#### **B. dim_match_mapping** (Match ID Translation)

| StatsBomb Match ID | CSV Match ID | Match Date | Teams | Status |
|------------------|--------------|-----------|-------|--------|
| 15500 | 123456 | 2023-08-12 | Arsenal vs Fulham | MAPPED |
| 15501 | 123457 | 2023-08-12 | Manchester City vs West Ham | MAPPED |
| ... | ... | ... | ... | ... |

**What you need to do:**
- Read matches from staging (stg_e0_match_raw)
- Read StatsBomb match metadata (from JSON files)
- Match on: Match date + Team names (both sides)
- Create INSERT script: `create_mapping_tables.sql`
- Result: 380 match mappings (StatsBomb ↔ CSV)

**Why this matters:**
- StatsBomb events have only StatsBomb match IDs
- CSV matches have only CSV match IDs
- You need to translate StatsBomb events to CSV matches
- Without mapping, events are orphaned (unmatched to real matches)

**Example logic:**
```sql
INSERT INTO dim_match_mapping (statsbomb_match_id, csv_match_id, match_date, home_team, away_team)
SELECT 
    je.match_id AS statsbomb_match_id,
    em.match_id AS csv_match_id,
    je.match_date,
    ht.team_name AS home_team,
    at.team_name AS away_team
FROM stg_events_raw je
JOIN stg_e0_match_raw em 
    ON DATE(je.match_date) = DATE(em.date)
    AND [match teams match logic]
JOIN dim_team ht ON je.home_team_id = ht.team_id
JOIN dim_team at ON je.away_team_id = ht.team_id;
```

**Deliverable 1 Checklist:**
- [ ] dim_team_mapping: 40+ rows (StatsBomb ↔ DWH team IDs)
- [ ] dim_match_mapping: 380+ rows (StatsBomb ↔ CSV match IDs)
- [ ] Mapping script runs without errors
- [ ] All mappings validated (both sides exist)
- [ ] No NULL mappings (complete coverage)
- [ ] Tested with staging data

---

### **DELIVERABLE 2: Fact Tables** 📊

#### **A. fact_match** (Match-Level Data)

| match_id | match_date | season_id | home_team_id | away_team_id | home_goals | away_goals | venue_id | referee_id |
|----------|-----------|-----------|--------------|--------------|-----------|-----------|----------|-----------|
| 1 | 2023-08-12 | 1 | 1 | 2 | 1 | 0 | 1 | 1 |
| 2 | 2023-08-12 | 1 | 3 | 4 | 2 | 1 | 2 | 2 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Granularity:** One row per match (830 rows total)

**Source:** CSV data (stg_e0_match_raw)

**What you need to do:**
```sql
-- Create load_fact_match.sql

INSERT INTO fact_match (match_date, season_id, home_team_id, away_team_id, home_goals, away_goals, venue_id, referee_id)
SELECT 
    stg.date AS match_date,
    ds.season_id,
    dtm.dwh_team_id AS home_team_id,
    dtm2.dwh_team_id AS away_team_id,
    stg.home_goals,
    stg.away_goals,
    ds2.stadium_id,
    dr.referee_id
FROM stg_e0_match_raw stg
JOIN dim_season ds ON YEAR(stg.date) = ds.season_year
JOIN dim_team_mapping dtm ON stg.home_team_id = dtm.statsbomb_team_id
JOIN dim_team_mapping dtm2 ON stg.away_team_id = dtm2.statsbomb_team_id
LEFT JOIN dim_stadium ds2 ON stg.venue = ds2.stadium_name
LEFT JOIN dim_referee dr ON stg.referee_name = dr.referee_name
WHERE stg.date IS NOT NULL;
```

**Deliverable 2A Checklist:**
- [ ] fact_match loads 830 rows (one per CSV match)
- [ ] All match dates populated
- [ ] All team IDs populated (no NULLs for teams)
- [ ] All season IDs correct
- [ ] Goal counts match source
- [ ] Foreign keys all valid (no orphaned records)
- [ ] Tested and validated

---

#### **B. fact_match_events** (Event-Level Data) 🔴 MOST COMPLEX

| event_id | match_id | event_timestamp | player_id | team_id | event_type | x_position | y_position | outcome |
|----------|----------|-----------------|-----------|---------|-----------|-----------|-----------|---------|
| 1 | 1 | 00:00:15 | 123 | 1 | Pass | 50.5 | 30.2 | Successful |
| 2 | 1 | 00:00:18 | 124 | 1 | Pass | 55.3 | 32.1 | Successful |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Granularity:** One row per event (1.3M+ rows)

**Source:** StatsBomb JSON files (stg_events_raw)

**Why this is 🔴 HARD:**
1. **1.3M+ rows** - Requires efficient loading, proper indexing
2. **Multi-step process** - 4 separate SQL scripts (see below)
3. **Deduplication** - Must prevent duplicate events on re-runs
4. **Mapping logic** - Must use dim_match_mapping to connect to fact_match
5. **Data validation** - Must reconcile with match data

**The 4-Step Loading Process:**

**Step 1:** Create temporary aggregation table
```sql
-- load_fact_match_events_step1.sql
-- Purpose: Create working table to track load progress

CREATE TEMPORARY TABLE temp_event_load AS
SELECT 
    stg.event_id,
    stg.match_id AS statsbomb_match_id,
    stg.event_timestamp,
    stg.event_type,
    COUNT(*) as event_count
FROM stg_events_raw stg
GROUP BY stg.match_id, stg.event_timestamp
ORDER BY stg.match_id;
```

**Step 2:** Verify match mappings exist
```sql
-- load_fact_match_events_step2.sql
-- Purpose: Ensure all StatsBomb matches have CSV equivalents

SELECT 
    COUNT(*) as unmapped_matches
FROM (
    SELECT DISTINCT je.match_id
    FROM stg_events_raw je
    LEFT JOIN dim_match_mapping mm ON je.match_id = mm.statsbomb_match_id
    WHERE mm.csv_match_id IS NULL
) x;

-- This should return 0 (all events mapped to matches)
-- If > 0, there are orphaned events!
```

**Step 3:** Load events with deduplication ⭐ CRITICAL
```sql
-- load_fact_match_events_step3_final.sql
-- Purpose: Load 1.3M events, with deduplication via manifest

INSERT INTO fact_match_events 
    (match_id, event_timestamp, player_id, team_id, event_type, x_position, y_position, outcome)
SELECT 
    mm.csv_match_id,
    je.event_timestamp,
    COALESCE(dp.player_id, -1) AS player_id,  -- Use sentinel if player unknown
    COALESCE(dtm.dwh_team_id, -1) AS team_id,  -- Use sentinel if team unknown
    je.event_type,
    je.x_position,
    je.y_position,
    je.outcome
FROM stg_events_raw je
JOIN dim_match_mapping mm ON je.match_id = mm.statsbomb_match_id
LEFT JOIN dim_team_mapping dtm ON je.team_id = dtm.statsbomb_team_id
LEFT JOIN dim_player dp ON je.player_id = dp.statsbomb_player_id
WHERE NOT EXISTS (
    -- Check manifest: has this event been loaded before?
    SELECT 1 
    FROM etl_json_manifest ejm 
    WHERE ejm.json_file = je.source_file
        AND ejm.event_id_range_start <= je.event_id
        AND ejm.event_id_range_end >= je.event_id
)
ORDER BY je.match_id, je.event_timestamp;

-- AFTER successful insert, log to manifest
INSERT INTO etl_json_manifest (json_file, event_id_range_start, event_id_range_end, row_count, load_status)
SELECT 
    je.source_file,
    MIN(je.event_id),
    MAX(je.event_id),
    COUNT(*),
    'LOADED'
FROM stg_events_raw je
WHERE NOT EXISTS (SELECT 1 FROM etl_json_manifest WHERE json_file = je.source_file)
GROUP BY je.source_file;
```

**Why deduplication matters:**
- Run the pipeline twice = events loaded ONLY ONCE ✅
- Without manifest: duplicate inserts ❌
- With manifest: safe re-runs 🟢

**Step 4:** Verify load success
```sql
-- load_fact_match_events_step4_verify.sql
-- Purpose: Validate all events loaded correctly

-- Check event count
SELECT COUNT(*) as total_events FROM fact_match_events;
-- Expected: ~1.3M+ (2,675,770 for full dataset)

-- Check no orphaned events (all have valid match_id)
SELECT COUNT(*) as orphaned_events
FROM fact_match_events fme
WHERE NOT EXISTS (SELECT 1 FROM fact_match fm WHERE fm.match_id = fme.match_id);
-- Expected: 0

-- Check no orphaned players (all players exist or are sentinel -1)
SELECT COUNT(*) as orphaned_players
FROM fact_match_events fme
WHERE NOT EXISTS (SELECT 1 FROM dim_player dp WHERE dp.player_id = fme.player_id)
    AND fme.player_id != -1;
-- Expected: 0

-- Check no orphaned teams (all teams exist or are sentinel -1)
SELECT COUNT(*) as orphaned_teams
FROM fact_match_events fme
WHERE NOT EXISTS (SELECT 1 FROM dim_team dt WHERE dt.team_id = fme.team_id)
    AND fme.team_id != -1;
-- Expected: 0

-- Reconciliation: events per match
SELECT 
    fm.match_id,
    COUNT(fme.event_id) as event_count,
    CASE 
        WHEN COUNT(fme.event_id) > 1000 THEN 'High activity match'
        WHEN COUNT(fme.event_id) > 500 THEN 'Normal match'
        ELSE 'Low activity match'
    END as match_type
FROM fact_match fm
LEFT JOIN fact_match_events fme ON fm.match_id = fme.match_id
GROUP BY fm.match_id
ORDER BY event_count DESC;
```

**Deliverable 2B Checklist:**
- [ ] Step 1: Temp table creates without errors
- [ ] Step 2: All matches mapped (0 unmapped)
- [ ] Step 3: 1.3M+ events inserted successfully
- [ ] Step 4: All validation queries pass (0 orphans)
- [ ] Deduplication works (run twice, same count both times)
- [ ] Tested with `--limit-data 10` first (quick validation)
- [ ] Tested with full data
- [ ] etl_json_manifest shows all files loaded

---

#### **C. fact_player_stats** (Player Performance Data)

| player_stats_id | match_id | player_id | team_id | minutes_played | goals | assists | xg | xa | shots | shots_on_target |
|-----------------|----------|-----------|---------|-----------------|-------|---------|-----|-----|-------|-----------------|
| 1 | 1 | 123 | 1 | 90 | 1 | 2 | 2.1 | 1.5 | 5 | 2 |
| 2 | 1 | 124 | 1 | 45 | 0 | 0 | 0.5 | 0.2 | 2 | 1 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Granularity:** One row per player per match (1,600+ rows)

**Source:** FBRef/mock data (stg_player_stats_fbref)

**What you need to do:**
```sql
-- load_fact_player_stats.sql

INSERT INTO fact_player_stats 
    (match_id, player_id, team_id, minutes_played, goals, assists, xg, xa, shots, shots_on_target)
SELECT 
    fm.match_id,
    COALESCE(dp.player_id, -1) AS player_id,
    COALESCE(dtm.dwh_team_id, -1) AS team_id,
    stg.minutes_played,
    stg.goals,
    stg.assists,
    stg.xg,
    stg.xa,
    stg.shots,
    stg.shots_on_target
FROM stg_player_stats_fbref stg
JOIN fact_match fm ON fm.match_id = stg.match_id  -- Join to fact_match
LEFT JOIN dim_player dp ON stg.player_name = dp.player_name AND stg.team_name = dp.team_name
LEFT JOIN dim_team_mapping dtm ON stg.team_name = dtm.team_name
WHERE stg.minutes_played > 0;  -- Only include players who played
```

**Deliverable 2C Checklist:**
- [ ] fact_player_stats loads 1,600+ rows
- [ ] All foreign keys valid (match_id, player_id, team_id exist)
- [ ] Minutes, goals, assists, xG correctly populated
- [ ] No NULLs in critical columns
- [ ] Tested and validated

---

## 🔄 Deduplication System (The Secret to Not Having Duplicates!) ⭐

**Problem:** If you run the pipeline twice, what happens?
- **Without dedup:** 1.3M events inserted TWICE = 2.6M total (❌ BAD)
- **With dedup:** 1.3M events inserted ONCE = 1.3M total (✅ GOOD)

**Solution: ETL_Events_Manifest (Manifest Table)**

The manifest table tracks every JSON file you've already loaded:

```sql
-- Create etl_json_manifest table (Member 2 does this, but you POPULATE it)

CREATE TABLE etl_json_manifest (
    manifest_id INT PRIMARY KEY AUTO_INCREMENT,
    json_file VARCHAR(255) NOT NULL UNIQUE,  -- File name (e.g., "15500.json")
    event_id_range_start BIGINT,             -- First event ID in file
    event_id_range_end BIGINT,               -- Last event ID in file
    row_count INT,                            -- How many events in file
    load_status VARCHAR(20),                  -- 'LOADED', 'FAILED', 'PARTIAL'
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**How it works:**

**First run:**
```
Events in 15500.json: IDs 1-3500
├─ Check manifest: No record for "15500.json"
├─ Load events 1-3500 ✅
└─ Insert into manifest: json_file="15500.json", start=1, end=3500
```

**Second run (re-run same pipeline):**
```
Events in 15500.json: IDs 1-3500
├─ Check manifest: Found record for "15500.json"
├─ Skip loading (already loaded) ✅
└─ NO duplicate inserts!
```

**Your deduplication logic (Step 3):**
```sql
WHERE NOT EXISTS (
    SELECT 1 
    FROM etl_json_manifest ejm 
    WHERE ejm.json_file = je.source_file
)
-- This prevents re-loading already-loaded files
```

**Deliverable: Dedup Checklist:**
- [ ] Manifest table created and ready
- [ ] Load step checks manifest before inserting
- [ ] Test: Run pipeline twice with `--limit-data 10`
- [ ] Verify: Same row count both times (no duplicates)
- [ ] SQL query shows: 1st run = 36K events, 2nd run = 0 new events

---

## 📊 File Ownership (What You Modify)

```
MEMBER 4 OWNS THESE FILES (Only you modify):

src/sql/
├── create_mapping_tables.sql          ← Team & match mapping INSERT
├── load_fact_match.sql                ← CSV matches → fact_match
├── load_fact_match_events_step1.sql   ← Temp aggregation table
├── load_fact_match_events_step2.sql   ← Verify match mappings
├── load_fact_match_events_step3_final.sql  ← Load 1.3M events with dedup ⭐
├── load_fact_match_events_step4_verify.sql ← Validation queries
└── load_fact_player_stats.sql         ← Player stats → fact_player_stats

src/etl/
└── load_warehouse.py                  ← Python orchestration (you maintain)

YOU READ FROM (don't modify):
├── Staging tables (stg_events_raw, stg_e0_match_raw, stg_player_stats_fbref)
├── All dimensions (dim_team, dim_player, dim_referee, dim_date, dim_stadium, dim_season)
└── Mapping tables (once created)
```

**Golden Rule:** Only you touch fact-loading files. Nobody else modifies your SQL scripts.

---

## 🧪 Testing Strategy (Before Viva!)

### **Phase 1: Quick Validation** (Day 1-2, ~5 minutes)
```bash
# Test with 10 StatsBomb files (small dataset)
python -m src.etl.main --full-etl-and-facts --limit-data 10
```

**Expected results:**
- Stage data loads ✅
- Schema intact ✅
- Dimensions ready ✅
- fact_match: ~3 matches
- fact_match_events: ~10K events
- fact_player_stats: ~300 records

### **Phase 2: Mid-Scale Validation** (Day 2, ~2 minutes)
```bash
# Test with 30 StatsBomb files (bigger dataset)
python -m src.etl.main --full-etl-and-facts --limit-data 30
```

**Expected results:**
- All tables populated ✅
- fact_match: ~10 matches
- fact_match_events: ~33K events
- Mappings working ✅

### **Phase 3: Full Data Load** (Day 3, ~10 minutes)
```bash
# Load ALL 380 StatsBomb files
python -m src.etl.main --full-etl-and-facts
```

**Expected results:**
- fact_match: 830 matches ✅
- fact_match_events: 1.3M+ events ✅
- fact_player_stats: 1,600+ records ✅
- Zero FK violations ✅
- No orphaned records ✅

### **Phase 4: Deduplication Test** (Day 3, ~10 minutes)
```bash
# Run AGAIN to test dedup
python -m src.etl.main --full-etl-and-facts
```

**Expected results:**
- Same row counts as before ✅
- NO duplicate inserts ✅
- Manifest shows: No new events processed ✅

**Query to verify dedup:**
```sql
SELECT 
    'fact_match' as table_name, COUNT(*) as row_count FROM fact_match
UNION ALL
SELECT 'fact_match_events', COUNT(*) FROM fact_match_events
UNION ALL
SELECT 'fact_player_stats', COUNT(*) FROM fact_player_stats;
```

**Reconciliation query (check all events match to fact_match):**
```sql
-- Events per match should match between staging and facts
SELECT 
    COUNT(*) as total_events_in_facts,
    (SELECT COUNT(*) FROM stg_events_raw) as total_events_in_staging,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM stg_events_raw) THEN '✅ PERFECT MATCH'
        ELSE '⚠️ MISMATCH - Check dedup'
    END as status
FROM fact_match_events;
```

---

## 🎤 Your 8-Minute Viva Presentation

**You have exactly 8 minutes to present your work. Here's the structure:**

### **Slide 1: Overview (1 min)** 📌
```
TITLE: Facts, Mappings & Multi-Source Integration

WHAT YOU BUILT:
├─ Mapping tables (team ID translation, match ID translation)
├─ 3 fact tables (830 matches, 1.3M+ events, 1,600 player stats)
├─ Deduplication system (no duplicates on re-runs)
└─ Full referential integrity (zero orphaned records)

KEY NUMBER: 1.3M+ events loaded without a single duplicate ⭐
```

**Talking points:**
- "My work is the foundation of analytics in this DWH"
- "Everything that analysts query comes from my fact tables"
- "The hardest part: keeping 1.3M events synchronized with mappings"

---

### **Slide 2: The Problem - Multiple Data Sources (1.5 min)** 🔴
```
CHALLENGE: 2 Data Sources with Different IDs

Source 1: StatsBomb JSON
├─ Team ID: 217 = Manchester United
├─ Match ID: 15500
├─ Event IDs: 1 to 3,500 per match
└─ Data: 1.3M events

Source 2: FootballData.org CSV
├─ Team ID: 1 = Manchester United  
├─ Match ID: 123456
└─ Data: 830 matches

PROBLEM:
┌─────────────────────────────────┐
│ StatsBomb says: Team 217        │
│ CSV says: Team 1                │
│ MISMATCH! Which is correct? ❓  │
│                                 │
│ StatsBomb says: Match 15500     │
│ CSV says: Match 123456          │
│ But they're THE SAME MATCH! 🤔  │
└─────────────────────────────────┘

SOLUTION: Create mapping tables to translate IDs
```

**Talking points:**
- "Without mappings, StatsBomb events are orphaned"
- "I had to find the 'Rosetta Stone' between two ID systems"
- "Match mapping: found 380 exact matches between systems"

---

### **Slide 3: Mapping Tables - Your Solution (1.5 min)** 🗺️
```
MAPPING TABLE 1: dim_team_mapping

StatsBomb ID → DWH ID → Team Name
217         → 1      → Manchester United
218         → 2      → Manchester City
219         → 3      → Liverpool

Result: 40 team mappings (all EPL teams covered)

MAPPING TABLE 2: dim_match_mapping

StatsBomb Match ID → CSV Match ID → Date       → Teams
15500             → 123456      → 2023-08-12 → MU vs Fulham
15501             → 123457      → 2023-08-12 → City vs West Ham

Result: 380 match mappings (every StatsBomb match → CSV match)

HOW I MATCHED THEM:
├─ Join on: Match date + Team names (home and away)
├─ Verified: No unmatched events (100% coverage)
└─ Result: All 1.3M events now connected to real matches
```

**Talking points:**
- "Mapping is the glue that holds data from 2 sources together"
- "Without this, StatsBomb events would be disconnected from game results"
- "Achieved 380/380 match mappings (100% success rate)"

---

### **Slide 4: Fact Tables - The Data (1.5 min)** 📊
```
3 FACT TABLES YOU CREATED:

FACT 1: fact_match (830 rows)
├─ One row per match
├─ Columns: match_date, home_team_id, away_team_id, 
│           home_goals, away_goals, venue_id, referee_id
└─ Example: Man United 1-0 Fulham on 2023-08-12

FACT 2: fact_match_events (1,337,455 rows) ⭐ MAIN EVENT TABLE
├─ One row per event (pass, shot, foul, etc.)
├─ Columns: event_id, match_id, event_timestamp, 
│           player_id, team_id, event_type, x/y position, outcome
├─ Average: 1,600 events per match
└─ Loaded via 4-step process (robust, verified)

FACT 3: fact_player_stats (1,600 rows)
├─ One row per player per match
├─ Columns: match_id, player_id, team_id, minutes_played, 
│           goals, assists, xG, xA, shots, shots_on_target
└─ Example: Haaland scored 1 goal, 2 assists, 2.1 xG

TOTAL DATA VOLUME: 1.3M+ rows (830 + 1.3M + 1.6K)
```

**Talking points:**
- "fact_match_events is the largest table - contains every action in every match"
- "Each row is a moment in time (pass, shot, foul, etc.)"
- "All 1.3M events are now queryable and connected to match results"

---

### **Slide 5: The Multi-Step Loading Process (1.5 min)** 🔄
```
STEP 1: Create temp table
├─ Aggregate staging data by match
└─ Track load progress

STEP 2: Verify mappings ✅
├─ Check: All StatsBomb matches have CSV equivalents
├─ Result: 0 unmapped events (100% coverage)
└─ Confidence: All events will connect to fact_match

STEP 3: Load events with deduplication ⭐ CRITICAL
├─ Read from stg_events_raw (1.3M rows)
├─ Check: Has this event been loaded before?
├─ If NO: Insert into fact_match_events
├─ If YES: Skip (prevent duplicate)
├─ Log to manifest: Which files loaded
└─ Result: 1.3M events, zero duplicates

STEP 4: Verify success ✅
├─ Check: All events have valid match IDs (no orphans)
├─ Check: All players/teams exist (no FK violations)
├─ Check: Event counts match expectations
└─ Result: 100% data integrity validated
```

**Talking points:**
- "Why 4 steps? Because 1.3M rows need careful handling"
- "Step 2 catches problems BEFORE they happen"
- "Step 3's dedup system is the key to safe re-runs"
- "Step 4 validates before moving on"

---

### **Slide 6: Deduplication - The Secret Sauce (1 min)** 🔐
```
PROBLEM: What if you run the pipeline twice?

Without dedup:
└─ Run 1: Insert 1.3M events ✓
└─ Run 2: Insert 1.3M events AGAIN = 2.6M total ❌ DISASTER!

With dedup (manifest system):
└─ Run 1: Insert 1.3M events, record in manifest ✓
└─ Run 2: Check manifest, skip already-loaded files = 1.3M total ✓

HOW MANIFEST WORKS:
etl_json_manifest table tracks:
├─ json_file: "15500.json" 
├─ event_id_range: 1-3500 (events in this file)
├─ row_count: 3500
└─ load_status: 'LOADED'

Before inserting, check:
"Is this file already in the manifest?"
├─ If YES: Skip it (don't reload) ✓
└─ If NO: Load it (new file) ✓

RESULT: 
✅ Run pipeline 10 times = same 1.3M rows every time
✅ No duplicates, no orphans, no conflicts
✅ Safe to re-run without data corruption
```

**Talking points:**
- "Deduplication was the hardest problem I solved"
- "Without it, re-running the pipeline would double the data"
- "The manifest system is like a 'load history' - prevents re-loading"
- "Tested: Ran pipeline twice, got same row counts both times"

---

### **Slide 7: Validation & Metrics (1 min)** ✅
```
FINAL VALIDATION RESULTS:

fact_match:
├─ Loaded: 830 rows ✅
├─ FK valid: All home/away teams exist ✅
├─ FK valid: All season_ids exist ✅
└─ Goal: Yes, matches connect to events

fact_match_events:
├─ Loaded: 1,337,455 rows ✅
├─ FK valid: All match_ids exist in fact_match ✅
├─ FK valid: All player_ids exist in dim_player or are -1 (sentinel) ✅
├─ FK valid: All team_ids exist in dim_team or are -1 (sentinel) ✅
├─ Duplicates: ZERO ✅
└─ Orphaned records: ZERO ✅

fact_player_stats:
├─ Loaded: 1,600 rows ✅
├─ FK valid: All match_ids exist ✅
└─ FK valid: All player/team refs valid ✅

MANIFEST TRACKING:
├─ Files processed: 380 ✅
├─ Events tracked: 1,337,455 ✅
├─ Re-run test: No duplicates ✅
└─ Manifest entries: 380 ✅

PERFORMANCE:
├─ Time to load facts: ~5-7 minutes ✅
├─ Time for 2nd run (dedup): <30 seconds (skipped) ✅
└─ Query performance: Verified with large joins ✅

REFERENTIAL INTEGRITY:
├─ FK violations: ZERO ✅
├─ Orphaned events: ZERO ✅
├─ Orphaned players: ZERO ✅
└─ Data quality: 100% ✅
```

**Talking points:**
- "All validations passed - zero data quality issues"
- "1.3M rows, zero duplicates, zero orphans"
- "Tested performance, handles large joins efficiently"
- "Production ready for analytics"

---

### **Q&A Prep: Expected Questions** ❓

**Q1: "Why 1.3M events? What does that mean?"**  
A: "Each event is one action in a match - a pass, shot, foul, substitution, etc. With 380 matches and ~3,500 events per match, we get 1.3M total. Every piece of game action is tracked."

**Q2: "What if the mapping failed for a match?"**  
A: "I validated that 100% of matches mapped correctly. But as a safety measure, Step 2 checks for unmapped events - if any exist, the load stops and alerts me."

**Q3: "How did you prevent duplicates?"**  
A: "The manifest system in etl_json_manifest tracks every loaded file. Before inserting, we check: 'Have I loaded this file before?' If yes, skip. If no, load. I tested this by running the pipeline twice and verified no duplicate inserts."

**Q4: "What if a player wasn't found in the dimensions?"**  
A: "I use sentinel records (-1 for unknown). So if a StatsBomb player ID doesn't match to dim_player, I insert -1, maintaining referential integrity. This is better than rejecting the entire event."

**Q5: "Why use foreign keys if you have sentinels?"**  
A: "FK constraints ensure data quality. Sentinels (-1) are explicitly allowed because they represent 'unknown'. Regular NULLs would break the constraint, but -1 has a dimension row."

**Q6: "How would you scale to 10M events?"**  
A: "I'd partition the fact_match_events table by match_id, use parallel inserts (batch processing), and implement incremental loading instead of full reload. The manifest system already supports incremental updates."

**Q7: "Why the 4-step loading process?"**  
A: "Each step validates before proceeding. Step 1 prepares data, Step 2 catches mapping errors early, Step 3 loads with dedup, Step 4 validates integrity. Safer than 1 big SQL script."

**Q8: "What happens if step 3 fails halfway?"**  
A: "Each SQL script is its own transaction. If it fails, it rolls back entirely. The manifest only updates on success, so incomplete events aren't marked as loaded. Safe to retry."

---

## 🚀 Git Workflow (For You)

```bash
# 1. Create your feature branch
git checkout -b feature/member4-facts

# 2. Ensure you have latest from previous members
git checkout dev
git pull origin dev

# 3. Create your SQL scripts
# create_mapping_tables.sql
# load_fact_match.sql
# load_fact_match_events_step1.sql through step4_verify.sql
# load_fact_player_stats.sql

# 4. Test with small data
python -m src.etl.main --full-etl-and-facts --limit-data 10

# 5. Test with full data
python -m src.etl.main --full-etl-and-facts

# 6. Test deduplication (run again)
python -m src.etl.main --full-etl-and-facts

# 7. Commit your work
git add src/sql/load_fact_*.sql src/sql/create_mapping_tables.sql src/etl/load_warehouse.py
git commit -m "MEMBER 4: Fact tables & mappings - 1.3M events, zero duplicates, full dedup testing"

# 8. Push to your feature branch
git push origin feature/member4-facts

# 9. Create pull request to dev branch
# → Coordinator reviews and merges after testing
```

---

## 📋 Complete Checklist (Before Viva)

### **Part 1: Mapping Tables** ✅
- [ ] dim_team_mapping created (40 rows)
- [ ] dim_match_mapping created (380 rows)
- [ ] Mapping validation query passed (0 unmapped)
- [ ] Tested with staging data

### **Part 2: Fact Tables** ✅
- [ ] fact_match created and loaded (830 rows)
- [ ] fact_match_events created and loaded (1.3M+ rows)
- [ ] fact_player_stats created and loaded (1,600 rows)
- [ ] All FK constraints valid
- [ ] No orphaned records

### **Part 3: Deduplication** ✅
- [ ] etl_json_manifest table created
- [ ] Manifest check logic implemented in Step 3
- [ ] First run: 1.3M events loaded ✓
- [ ] Second run: 0 new events (dedup working) ✓
- [ ] Verified via manifest query

### **Part 4: Validation** ✅
- [ ] Step 1: Temp table created successfully
- [ ] Step 2: All matches mapped (0 unmapped)
- [ ] Step 3: Events loaded with dedup
- [ ] Step 4: All validation queries pass (0 orphans)
- [ ] Reconciliation: Events per match validated
- [ ] FK violations: ZERO
- [ ] Performance: Load time <10 minutes

### **Part 5: Documentation** ✅
- [ ] SQL scripts documented (comments explaining logic)
- [ ] Mapping strategy documented
- [ ] Aggregation logic documented
- [ ] Dedup system explained in README
- [ ] Troubleshooting guide created

### **Part 6: Viva Preparation** ✅
- [ ] Presentation slides created (7 slides)
- [ ] Talking points prepared for each slide
- [ ] Q&A responses prepared (8 expected questions)
- [ ] Demo ready (or recorded video)
- [ ] Timing practiced (exactly 8 minutes)
- [ ] Backup slides prepared (in case of detailed questions)

---

## 🎯 Summary

**Your Role:** Load 1.3M events from 2 data sources and make them queryable

**Your Deliverables:**
1. ✅ Mapping tables (translate IDs between systems)
2. ✅ 3 fact tables (1.3M+ rows, full referential integrity)
3. ✅ Deduplication system (safe re-runs, zero duplicates)
4. ✅ Validation (all data quality checks pass)
5. ✅ Documentation (how your system works)

**Your Challenge:** 🔴 Hard (complex logic, large scale, dedup system)

**Your Difficulty Level:** 🔴 HARD

**Estimated Time:** 3-5 days

**Viva Slot:** 8 minutes (present the solution, demo if possible)

**Key Success Metric:** 1.3M events loaded without a single duplicate ⭐

---

**Good luck! You're building the analytics foundation of this entire DWH.** 🚀

*EPL DWH - Member 4 Guide*  
*November 3, 2025*
