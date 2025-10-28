# ETL Command Sequence - IMPORTANT!

## ⚠️ The Problem
When you run `--load-fact-tables` ALONE, fact tables are empty because:
- `--load-fact-tables` expects `stg_e0_match_raw` to have 830 matches
- But those matches are only loaded by `--full-etl` or `--complete-player-pipeline`
- If you run `--complete-player-pipeline` first, it **cleans up the staging tables** before `--load-fact-tables` runs

## ✅ The Solution: Use CORRECT Command Sequence

### Option 1: RECOMMENDED - Single Command (Simplest)
```bash
# This does EVERYTHING in the right order:
# 1. Extract CSV/JSON/API data
# 2. Load into staging tables
# 3. Load into fact tables
# 4. Clean staging tables
.\.venv\Scripts\python.exe -m src.etl.main --complete-player-pipeline
```

### Option 2: Multi-stage (More Control)
```bash
# Step 1: Extract and stage data (DON'T clean yet)
.\.venv\Scripts\python.exe -m src.etl.main --full-etl

# Step 2: Load facts (while staging data still exists)
.\.venv\Scripts\python.exe -m src.etl.main --load-fact-tables

# Step 3: Load player stats
.\.venv\Scripts\python.exe -m src.etl.main --load-player-stats
```

### Option 3: Complete Re-extraction
```bash
# This loads ALL data fresh:
.\.venv\Scripts\python.exe -m src.etl.main --complete-player-pipeline
```

## ❌ DON'T DO THIS (Wrong Order)
```bash
# This will FAIL - staging tables already cleaned!
.\.venv\Scripts\python.exe -m src.etl.main --complete-player-pipeline
.\.venv\Scripts\python.exe -m src.etl.main --load-fact-tables  ← Staging empty now!
```

## 📊 What Each Command Does

### `--full-etl`
- ✅ Extracts CSV files → loads to `stg_e0_match_raw` (830 matches)
- ✅ Extracts JSON files → loads to `stg_events_raw` (1.3M events)
- ✅ Loads dimensions
- ✅ **CLEANS staging tables** at the end

### `--load-fact-tables`
- ❌ Does NOT extract any data
- ✅ Loads fact_match FROM `stg_e0_match_raw`
- ✅ Loads fact_match_events FROM `stg_events_raw`
- ⚠️ **Requires staging tables to already have data!**

### `--complete-player-pipeline`
- ✅ Extracts CSV files
- ✅ Loads staging tables
- ✅ Loads dimensions
- ✅ Loads player stats
- ✅ **CLEANS staging tables** at the end

## 🎯 Current Database State

**Staging Tables:**
- stg_e0_match_raw: 0 rows ← Empty (cleaned after previous run)
- stg_events_raw: 1,313,783 rows ← Has data from JSON extraction
- stg_player_raw: 0 rows ← Cleaned
- stg_player_stats_fbref: 0 rows ← Cleaned
- stg_team_raw: 0 rows ← Cleaned
- stg_referee_raw: 32 rows ← From Excel

**Fact Tables:**
- fact_match: 0 rows ← Can't load (needs stg_e0_match_raw with data)
- fact_match_events: 0 rows ← Can't load (needs fact_match)
- fact_player_stats: 0 rows ← Can't load

## 🔄 What You Need to Do NOW

To load fact tables, you MUST have CSV data in staging first:

```bash
# Re-extract and stage CSV data (this loads stg_e0_match_raw)
.\.venv\Scripts\python.exe -m src.etl.main --full-etl

# NOW load the facts (stg_e0_match_raw has 830 matches)
.\.venv\Scripts\python.exe -m src.etl.main --load-fact-tables
```

After this:
- ✅ fact_match: 830 rows (from CSV)
- ✅ fact_match_events: ~1.3M rows (from JSON events)
- ✅ fact_player_stats: ~1600 rows (from player stats)

---

**Key Takeaway:** `stg_e0_match_raw` MUST have data before running `--load-fact-tables`!
