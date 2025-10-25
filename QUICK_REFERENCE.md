# Quick Reference Card - EPL DWH

**Project:** English Premier League Data Warehouse  
**Status:** ✅ Production Ready  
**Date:** October 26, 2025

---

## 🚀 Quick Start (Copy-Paste)

```powershell
# 1. Start database
docker-compose up -d

# 2. Activate Python
.\.venv\Scripts\Activate.ps1

# 3. Run ETL
python -m src.etl.main --full-etl
python -m src.etl.main --load-fact-tables

# Done! ✅ 1.36M events loaded
```

---

## 📋 CLI Commands Cheat Sheet

| Command | What It Does | Time |
|---------|-------------|------|
| `--test-db` | Test DB connection | 1s |
| `--full-etl` | Staging + Dimensions | 5-10m |
| `--staging` | Raw data only | 2-5m |
| `--warehouse` | Dimensions only | 2-3m |
| `--load-fact-tables` | **Load 1.36M events** | **12m** |

---

## 📊 What Gets Loaded

**Dimensions (44,290 rows)**
- Dates (17,533 calendar days)
- Teams (20 EPL + UNKNOWN)
- Players (6,809 + UNKNOWN)
- Referees (33)
- Stadiums (58)
- Seasons (7)

**Facts (1,362,407 rows)**
- **Matches:** 830 from CSV
- **Events:** 1,362,577 from StatsBomb
  - Passes: 694,596
  - Carries: 534,227
  - + 100 other event types

**Mappings (724 rows)**
- Match mapping: 684 CSV↔StatsBomb pairs
- Team mapping: 40 team ID translations

---

## 🗂️ Documentation Quick Links

| Need | Read |
|------|------|
| Quick overview | [README.md](README.md) |
| Step-by-step guide | [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md) |
| SQL scripts | [SQL_SCRIPTS_REFERENCE.md](SQL_SCRIPTS_REFERENCE.md) |
| CLI command | [LOAD_FACT_TABLES_GUIDE.md](LOAD_FACT_TABLES_GUIDE.md) |
| Big picture | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| Where to find things | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| Final status | [FINAL_COMPLETE_STATUS.md](FINAL_COMPLETE_STATUS.md) |

---

## 🗄️ Database Connection

```
Host:     localhost
Port:     3307
User:     root
Password: 1234
Database: epl_dw
```

---

## 📝 SQL Scripts (In Order)

```
1. create_schema.sql                    (21 tables)
2. [Python] Load staging               (1.3M rows)
3. [Python] Load dimensions            (44K rows)
4. load_fact_match.sql                 (830 rows)
5. load_fact_match_events_step1.sql    (temp table)
6. load_fact_match_events_step2.sql    (validation)
7. load_fact_match_events_step3_final.sql (1.36M rows) ⭐
8. load_fact_match_events_step4_verify.sql (check)
9. final_row_count.sql                 (summary)
```

---

## 🎯 Common Tasks

### Run Everything
```powershell
python -m src.etl.main --full-etl
python -m src.etl.main --load-fact-tables
```

### Just Load Events
```powershell
# (after dimensions are loaded)
python -m src.etl.main --load-fact-tables
```

### Just Load Matches
```powershell
docker exec epl_mysql bash -c \
  "mysql -u root -p1234 epl_dw < src/sql/load_fact_match.sql"
```

### Check Database State
```powershell
docker exec epl_mysql bash -c \
  "mysql -u root -p1234 epl_dw < src/sql/final_row_count.sql"
```

### Connect to Database
```bash
mysql -u root -p1234 -h localhost --port=3307 epl_dw
```

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Activate venv: `.\.venv\Scripts\Activate.ps1` |
| DB connection fails | Start Docker: `docker-compose up -d` |
| Timeout on event load | Use `--load-fact-tables` (uses mapping tables) |
| FK violations | Check dimensions are loaded first |
| Script not found | Run from project root directory |

---

## ✅ Success Indicators

- [x] Docker container running
- [x] Python venv activated
- [x] `--full-etl` completes without errors
- [x] `--load-fact-tables` loads 1.36M rows
- [x] `final_row_count.sql` shows 1,362,577 events
- [x] Zero FK constraint violations

---

## 📞 Need Help?

1. Check [README.md](README.md) for overview
2. Read [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
3. See specific guide based on your issue
4. Check [SQL_SCRIPTS_REFERENCE.md#troubleshooting](SQL_SCRIPTS_REFERENCE.md)

---

## 🎓 Learning Resources

**Want to understand the ETL process?**
→ [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md) (complete explanation)

**Want to learn data warehouse design?**
→ [PROJECT_SUMMARY.md#architecture-overview](PROJECT_SUMMARY.md#architecture-overview)

**Want to see the SQL?**
→ [SQL_SCRIPTS_REFERENCE.md](SQL_SCRIPTS_REFERENCE.md)

---

## 🚢 Production Readiness

- ✅ All 1.36M events loaded
- ✅ Zero data quality issues
- ✅ Optimized performance
- ✅ Comprehensive documentation
- ✅ Error handling implemented
- ✅ Ready for deployment

---

**Last Updated:** October 26, 2025  
**Version:** 1.1  
**Status:** ✅ Production Ready
