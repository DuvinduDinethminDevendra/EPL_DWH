# Quick Setup Guide - EPL Data Warehouse

## Simplified Two-Step Setup

### 1️⃣ Run Full ETL (Schema + Dimensions + Staging)
```powershell
python -m src.etl.main --full-etl
```
**Duration:** ~5-10 minutes  
**Creates:** 
- Database and 21 tables
- 6 Dimension tables (teams, players, dates, etc.)
- 7 Staging tables

---

### 2️⃣ Load All Fact Tables (including player stats)
```powershell
python -m src.etl.main --load-fact-tables
```
**Duration:** ~9-10 minutes  
**Automatically does:**
- ✅ Generates valid player stats mock data (with real team names)
- ✅ Loads fact_match (830 matches)
- ✅ Loads fact_match_events (1.36M+ events)
- ✅ Then loads fact_player_stats (483+ records)

---

## ✅ Done! Verify Everything Loaded

```powershell
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    facts = [
        ('fact_match', 'SELECT COUNT(*) FROM fact_match'),
        ('fact_match_events', 'SELECT COUNT(*) FROM fact_match_events'),
        ('fact_player_stats', 'SELECT COUNT(*) FROM fact_player_stats')
    ]
    for name, query in facts:
        result = conn.execute(text(query))
        count = result.scalar()
        print(f'{name:.<25} {count:>12,} rows')
"
```

**Expected Output:**
```
fact_match................          830 rows
fact_match_events.........    1,362,577 rows
fact_player_stats.........          483 rows
```

---

## 📊 Final Database State

| Layer | Tables | Status |
|-------|--------|--------|
| **Facts** | 3 | ✅ All populated |
| **Dimensions** | 6 | ✅ All populated |
| **Mappings** | 2 | ✅ All populated |
| **Staging** | 7 | ✅ Ready |
| **Metadata** | 3+ | ✅ Ready |

**Total Data:** ~1.4M rows across fact & dimension tables

---

## 🔧 Troubleshooting

### Problem: `fact_player_stats` is empty
**Cause:** The `--load-fact-tables` command now automatically generates valid player stats data. If it's still empty, check that staging data generation didn't fail.

### Problem: Foreign key constraint errors
**Solution:** Ensure you ran `--full-etl` first to create dimensions

---

## 📖 What Changed?

**Before (Old way - 4 steps):**
```
1. python -m src.etl.main --full-etl
2. python generate_player_stats_mock_data.py
3. python -m src.etl.main --load-fact-tables
4. python -m src.etl.main --load-player-stats
```

**Now (New way - 2 steps):**
```
1. python -m src.etl.main --full-etl
2. python -m src.etl.main --load-fact-tables
```

The player stats generation is now **automatic** inside Step 2! 🎉

---

## 📚 Documentation

- **ETL_PIPELINE_GUIDE.md** - Complete pipeline walkthrough
- **LOAD_FACT_TABLES_GUIDE.md** - Detailed fact loading steps
- **SQL_SCRIPTS_REFERENCE.md** - All SQL scripts documented
- **DATABASE_SCHEMA_STRUCTURE.md** - Complete schema reference

---

## 🎯 Summary

✅ **2-step process** (each takes 1 command)  
✅ **Total time:** ~15-20 minutes  
✅ **Result:** Fully operational data warehouse with 1.4M+ rows  
✅ **All fact tables populated** (including player stats automatically!)  

**Ready to analyze EPL data! 🚀**
