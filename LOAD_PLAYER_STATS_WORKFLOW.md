# Loading Player Stats - Correct Workflow

## Problem
When running `python -m src.etl.main --load-player-stats` for the first time, `fact_player_stats` stays empty because the staging table (`stg_player_stats_fbref`) contains invalid team/player names that don't match the dimensions.

## Solution
You must pre-populate the staging table with valid EPL team and player names **before** loading facts.

## Correct Order

### Step 1: Run Full ETL to create schema + dimensions
```powershell
python -m src.etl.main --full-etl
```
This creates:
- ✅ Database schema
- ✅ Dimensions (teams, players, dates, etc.)
- ✅ Fact tables (empty)
- ✅ Staging tables (empty)

### Step 2: Generate valid player stats mock data
```powershell
python generate_player_stats_mock_data.py
```
This:
- ✅ Clears `stg_player_stats_fbref`
- ✅ Inserts 1,600 records with **real** EPL team names and player names
- ✅ Makes the names match `dim_team` and `dim_player`

### Step 3: Load fact_match and fact_match_events
```powershell
python -m src.etl.main --load-fact-tables
```
This loads:
- ✅ fact_match (830 rows)
- ✅ fact_match_events (1.3M rows)

### Step 4: Now load player stats
```powershell
python -m src.etl.main --load-player-stats
```
Now it works! Because:
- ✅ Staging has valid team names → join to `dim_team` succeeds
- ✅ Staging has valid player names → join to `dim_player` succeeds
- ✅ Result: **fact_player_stats populated with 483 rows**

---

## Complete One-Time Setup

```powershell
# 1. Full ETL
python -m src.etl.main --full-etl

# 2. Generate mock data with valid names
python generate_player_stats_mock_data.py

# 3. Load facts
python -m src.etl.main --load-fact-tables

# 4. Load player stats
python -m src.etl.main --load-player-stats
```

**Total time:** ~15-20 minutes

---

## What's Different?

| Component | Before | After |
|-----------|--------|-------|
| Mock data quality | ❌ Invalid team names | ✅ Real EPL teams |
| Player data | ❌ Generic names | ✅ Real player names |
| Joins work | ❌ No matches | ✅ Proper lookups |
| fact_player_stats | ❌ 0 rows | ✅ 483 rows |

---

## Why This Happens

The `--full-etl` command generates synthetic player stats but doesn't know the exact EPL team names. The `generate_player_stats_mock_data.py` script uses the exact team names from `dim_team`, ensuring perfect join matches.

**Key lesson:** When working with dimensional data, staging data must use the **exact same values** as the dimension tables for foreign keys to work.

---

## Files

- `generate_player_stats_mock_data.py` — Generates valid mock data (run before `--load-player-stats`)
- `src/etl/main.py` — Main ETL orchestrator
- `src/sql/load_fact_player_stats.sql` — SQL for loading facts
