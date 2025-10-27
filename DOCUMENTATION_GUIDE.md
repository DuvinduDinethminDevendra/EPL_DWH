# 📚 EPL DWH Documentation Guide

**Quick Navigation for Different User Types**

---

## 🆕 **START HERE**

### First Time Using EPL DWH?
```
1. Read README.md (5 min)           → Overview of the project
2. Check Quick Start section         → Get database running
3. Run maintenance/verification      → Confirm everything works
```

### Need to Run the Pipeline?
```
1. Open MAINTENANCE.md
2. Find "Daily Operations" section
3. Follow the commands
```

### Something Broken?
```
1. Open MAINTENANCE.md
2. Jump to "Troubleshooting" section
3. Find your error message
4. Follow the solution steps
```

---

## 📖 **Documentation Map**

```
┌─────────────────────────────────────────────────────┐
│  README.md ← PROJECT OVERVIEW (START HERE)          │
│  • Quick start instructions                         │
│  • Current data state                               │
│  • Key features explained                           │
│  • Sentinel strategy basics                         │
└─────────────────────────────────────────────────────┘
         ↓                      ↓                    ↓
    ┌─────────────┐  ┌──────────────┐  ┌───────────────┐
    │ MAINTENANCE │  │   PROJECT    │  │  GETTING      │
    │    .md      │  │   STATUS     │  │  STARTED      │
    │             │  │    .md       │  │   GUIDES      │
    │ Operations  │  │              │  │               │
    │ & Trouble-  │  │ Status &     │  │ ETL_PIPELINE  │
    │ shooting    │  │ Inventory    │  │ _GUIDE.md     │
    │ (12 KB)     │  │ (9 KB)       │  │ (29 KB)       │
    └─────────────┘  └──────────────┘  │               │
         ↓                ↓              │ LOAD_FACT    │
    ┌─────────────────────────────────┐ │ _TABLES_     │
    │  REFERENCE DOCUMENTATION        │ │ GUIDE.md     │
    │                                 │ │ (17 KB)      │
    │  • SQL_SCRIPTS_REFERENCE.md     │ │               │
    │  • DATABASE_SCHEMA_STRUCTURE.md │ │ QUICK_SETUP  │
    │  • LOAD_PLAYER_STATS_WORKFLOW   │ │ _GUIDE.md    │
    │                                 │ │ (3 KB)       │
    └─────────────────────────────────┘ └───────────────┘
```

---

## 👥 **Choose Your Role**

### 🚀 **New Developer / Fresh Start**
**Goal:** Get the project running locally

**Read in order:**
1. **README.md** (5 min) - Understand what this is
2. **QUICK_SETUP_GUIDE.md** (5 min) - Get database running
3. **MAINTENANCE.md** → "Daily Operations" (5 min) - Run the ETL
4. **PROJECT_STATUS.md** (10 min) - Understand current state

**Expected time:** ~25 minutes to get operational

---

### 🔧 **Operations / DevOps Engineer**
**Goal:** Maintain and troubleshoot the system

**Read in order:**
1. **README.md** → "Sentinel Strategy" section (3 min)
2. **MAINTENANCE.md** (20 min) - Complete guide
   - Startup/shutdown procedures
   - Reset scenarios
   - Troubleshooting section
3. **PROJECT_STATUS.md** → "Maintenance Schedule" (5 min)

**Key scripts to know:**
```powershell
truncate.py                    # Reset data (keeps sentinels)
add_sentinels2.py              # Ensure sentinels exist
check_sentinels_and_counts.py  # Verify data integrity
```

**Expected time:** ~30 minutes to mastery

---

### 👨‍💼 **Project Manager / Tech Lead**
**Goal:** Understand status and project health

**Read in order:**
1. **README.md** → "Current Data State" section (5 min)
2. **PROJECT_STATUS.md** (15 min)
   - Executive Summary
   - Current Data Inventory
   - Known Limitations
   - Production Recommendations
3. **MAINTENANCE.md** → "Performance Monitoring" (5 min)

**Key metrics to track:**
- Row counts in fact tables
- Any FK constraint violations
- ETL execution time
- Last successful run date

**Expected time:** ~25 minutes

---

### 🏗️ **Data Engineer / Architect**
**Goal:** Deep understanding of the system design

**Read in order:**
1. **README.md** - Full document (10 min)
2. **ETL_PIPELINE_GUIDE.md** (30 min) - Complete process walkthrough
3. **DATABASE_SCHEMA_STRUCTURE.md** (20 min) - Schema deep dive
4. **LOAD_FACT_TABLES_GUIDE.md** (15 min) - Fact loading logic
5. **SQL_SCRIPTS_REFERENCE.md** (15 min) - SQL details

**Consider modifying:**
- Batch sizes in `src/etl/load/load_facts.py`
- Sentinel values if needed
- Index strategies for large data volumes

**Expected time:** ~90 minutes for complete understanding

---

### 🐛 **Troubleshooting Someone's Issue**
**Goal:** Diagnose and fix problems quickly

**Process:**
1. Ask user what error they see
2. Go to **MAINTENANCE.md** → "Troubleshooting" section
3. Find matching error message
4. Follow solution steps
5. If not in troubleshooting:
   - Check "Quick Reference" table
   - Check "Backup & Recovery" for data issues
   - Check "Performance Monitoring" if slow

**Common scenarios:**
- **FK Violation** → "Issue: FK Constraint Violations"
- **Can't connect** → "Issue: Can't Connect to MySQL"
- **Data missing** → "Data Reset Procedures"
- **Performance** → "Issue: Out of Memory"
- **Hangs** → "Issue: ETL Hangs"

**Expected time:** 5-30 minutes depending on issue

---

## 🎯 **Documentation by Task**

### Running the Pipeline
```
README.md → "Quick Start" section
                ↓
MAINTENANCE.md → "Daily Operations" section
                ↓
Run: python -m src.etl.main --full-etl
     python -m src.etl.main --load-fact-tables
                ↓
Run: python check_sentinels_and_counts.py
```

### Resetting Data
```
MAINTENANCE.md → "Data Reset Procedures" section
                ↓
Choose your scenario:
  1. Full fresh start (keep sentinels)
  2. Complete clean slate
  3. Staging-only reset
                ↓
Follow step-by-step instructions
                ↓
Verify with: python check_sentinels_and_counts.py
```

### Fixing FK Violations
```
MAINTENANCE.md → "Troubleshooting" → "Issue: FK Constraint Violations"
                ↓
1. Run: python add_sentinels2.py
2. Run: python -m src.etl.main --load-fact-tables
3. Verify: python check_sentinels_and_counts.py
```

### Understanding Sentinel Strategy
```
README.md → "Sentinel Strategy" section
                ↓
Learn:
  • Why -1 and 6808 exist
  • Which tables use which sentinels
  • How to filter them out
```

---

## 📋 **File Organization**

### 🟦 **Core Documentation** (Read these)
| File | Purpose | Read Time |
|------|---------|-----------|
| README.md | Project overview | 10 min |
| MAINTENANCE.md | Operations guide | 20 min |
| PROJECT_STATUS.md | Status report | 15 min |
| DOCUMENTATION_SUMMARY.md | What was updated | 5 min |

### 🟨 **Technical Reference** (Lookup as needed)
| File | Purpose | Read Time |
|------|---------|-----------|
| ETL_PIPELINE_GUIDE.md | How ETL works | 30 min |
| LOAD_FACT_TABLES_GUIDE.md | How facts load | 15 min |
| SQL_SCRIPTS_REFERENCE.md | SQL details | 15 min |
| DATABASE_SCHEMA_STRUCTURE.md | Schema details | 20 min |

### 🟩 **Quick Guides** (Quick reference)
| File | Purpose | Read Time |
|------|---------|-----------|
| QUICK_SETUP_GUIDE.md | Get started quickly | 5 min |
| LOAD_PLAYER_STATS_WORKFLOW.md | Player stats demo | 5 min |

---

## ⚡ **Quick Reference Commands**

```powershell
# Start database
docker-compose up -d

# Test connection
python -m src.etl.main --test-db

# Run full ETL
python -m src.etl.main --full-etl          # ~7 min
python -m src.etl.main --load-fact-tables  # ~6 min

# Reset data (safe - preserves sentinels)
python truncate.py

# Ensure sentinels exist
python add_sentinels2.py

# Verify data integrity
python check_sentinels_and_counts.py

# Stop database
docker-compose down
```

---

## 🔍 **Index by Problem Type**

### Data Problems
- Table empty → README "Sentinel Strategy" + MAINTENANCE "Data Reset"
- FK violations → MAINTENANCE "Troubleshooting" → "Issue: FK Constraint Violations"
- Wrong row counts → PROJECT_STATUS "Data Inventory" + verification script
- Missing sentinels → Run `python add_sentinels2.py`

### Connection Problems
- Can't connect → MAINTENANCE "Troubleshooting" → "Issue: Can't Connect"
- Database not running → MAINTENANCE "Startup & Shutdown"
- Port already in use → docker-compose down, then try again

### Performance Problems
- Pipeline too slow → MAINTENANCE "Performance Monitoring"
- Out of memory → MAINTENANCE "Troubleshooting" → "Issue: Out of Memory"
- CPU pegged → Check Docker stats with `docker stats epl_mysql`

### Documentation Problems
- Can't find something → This file (DOCUMENTATION_GUIDE.md)
- Confused about structure → See "Documentation Map" above
- Need architecture details → ETL_PIPELINE_GUIDE.md + DATABASE_SCHEMA_STRUCTURE.md

---

## 📞 **Getting Help**

### If something isn't working:
1. Check MAINTENANCE.md troubleshooting section
2. Run `python check_sentinels_and_counts.py` to see current state
3. Check PROJECT_STATUS.md for known limitations
4. Review error message in terminal output
5. Try suggested fix in MAINTENANCE.md

### If documentation is unclear:
1. Check if there's a more specific guide (use "Index by Problem Type" above)
2. Look at code comments in `src/etl/main.py`
3. Run a quick test to see actual behavior
4. Reference DATABASE_SCHEMA_STRUCTURE.md for schema details

### If still stuck:
1. Review MAINTENANCE.md → "Best Practices"
2. Check recent git commits for context
3. Run database verification to confirm current state
4. Try "Complete Clean Slate" reset procedure

---

## ✅ **Checklist Before Production**

- [ ] Read README.md completely
- [ ] Read MAINTENANCE.md "Best Practices" section
- [ ] Run full ETL pipeline successfully
- [ ] Verify sentinels exist: `python check_sentinels_and_counts.py`
- [ ] Set up backup procedure: MAINTENANCE.md "Backup & Recovery"
- [ ] Document any custom modifications
- [ ] Configure monitoring/alerting per MAINTENANCE.md recommendations
- [ ] Test disaster recovery procedure: "Complete Clean Slate" in MAINTENANCE.md

---

## 🎓 **Learning Path**

### Week 1: Basics
- [ ] Read README.md (5 min)
- [ ] Run setup from QUICK_SETUP_GUIDE.md (10 min)
- [ ] Get pipeline working (20 min)
- [ ] Read MAINTENANCE.md "Daily Operations" (10 min)

### Week 2: Deeper Understanding
- [ ] Read ETL_PIPELINE_GUIDE.md (30 min)
- [ ] Review SQL_SCRIPTS_REFERENCE.md (15 min)
- [ ] Understand sentinel strategy in depth (10 min)

### Week 3: Mastery
- [ ] Read DATABASE_SCHEMA_STRUCTURE.md (20 min)
- [ ] Study LOAD_FACT_TABLES_GUIDE.md (15 min)
- [ ] Do a full reset using MAINTENANCE.md (15 min)
- [ ] Practice troubleshooting from MAINTENANCE.md (30 min)

### Week 4+: Production Ready
- [ ] Implement monitoring & alerts
- [ ] Set up automated backups
- [ ] Document custom modifications
- [ ] Plan scaling strategy per PROJECT_STATUS.md recommendations

---

**Total Documentation:** ~200 KB across 10 comprehensive guides  
**Organized for:** Quick access, specific searches, complete learning  
**Updated:** October 27, 2025  
**Status:** ✅ Production Ready
