# EPL DWH - Maintenance & Operations Guide

**Last Updated:** October 27, 2025  
**Status:** ✅ Production Ready

This guide covers common maintenance tasks, troubleshooting, and operational procedures for the EPL Data Warehouse.

---

## Table of Contents

1. [Startup & Shutdown](#startup--shutdown)
2. [Daily Operations](#daily-operations)
3. [Data Reset Procedures](#data-reset-procedures)
4. [Troubleshooting](#troubleshooting)
5. [Backup & Recovery](#backup--recovery)
6. [Performance Monitoring](#performance-monitoring)

---

## Startup & Shutdown

### Start the Database

```powershell
# Navigate to project root
cd d:\myPortfolioProject\EPL_DWH

# Start MySQL container
docker-compose up -d

# Verify container is running
docker ps | findstr epl_mysql
```

**Expected output:** Container named `epl_mysql` running on port `3307`

### Stop the Database

```powershell
# Graceful shutdown
docker-compose down

# Stop container only (keep data)
docker-compose stop

# Remove container entirely (keep data volume)
docker-compose down -v
```

### Verify Database Connection

```powershell
# Test from Python
python -m src.etl.main --test-db

# Expected output: [OK] Database connection successful
```

---

## Daily Operations

### Run Full ETL Pipeline

**One-command workflow:**

```powershell
# Activate virtualenv
.\.venv\Scripts\Activate.ps1

# Run full pipeline (extract + load dimensions + load facts)
python -m src.etl.main --full-etl          # ~5-7 minutes
python -m src.etl.main --load-fact-tables  # ~6 minutes
```

**Total time:** ~11-13 minutes

### Monitor Pipeline Progress

```powershell
# In a separate terminal, run:
python check_sentinels_and_counts.py
```

Or query directly:

```powershell
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    m = conn.execute(text('SELECT COUNT(*) FROM fact_match')).scalar()
    e = conn.execute(text('SELECT COUNT(*) FROM fact_match_events')).scalar()
    p = conn.execute(text('SELECT COUNT(*) FROM fact_player_stats')).scalar()
    print(f'Matches: {m} | Events: {e:,} | Player Stats: {p}')
"
```

---

## Data Reset Procedures

### Scenario 1: Full Fresh Start (Keep Sentinels)

**Use when:** You want to reload all data but preserve sentinel records.

```powershell
# 1. Truncate non-kept tables (dim_player, dim_team preserved)
python truncate.py

# 2. Ensure sentinels exist
python add_sentinels2.py

# 3. Run full ETL
python -m src.etl.main --full-etl

# 4. Load facts
python -m src.etl.main --load-fact-tables

# 5. Verify
python check_sentinels_and_counts.py
```

**Preserved:**
- `dim_player` (6,847 real + 2 sentinels: -1, 6808)
- `dim_team` (25 real + 1 sentinel: -1)
- `dim_date`, `dim_season`, mappings
- `fact_match_events` (existing events preserved)
- `ETL_Events_Manifest`, `stg_events_raw`

### Scenario 2: Complete Clean Slate (Nuclear Option)

**Use when:** Something is corrupted and you need everything fresh.

```powershell
# Stop container
docker-compose down

# Remove MySQL data volume (DESTRUCTIVE - all data lost)
docker volume rm epl_dwh_mysql_data

# Restart container (schema recreated)
docker-compose up -d

# Re-run full pipeline
python -m src.etl.main --full-etl
python -m src.etl.main --load-fact-tables
```

### Scenario 3: Staging-Only Reset

**Use when:** You want to re-process staging without touching dimensions or facts.

```powershell
# Truncate staging tables only
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    conn.execute(text('TRUNCATE TABLE stg_events_raw'))
    conn.execute(text('TRUNCATE TABLE stg_e0_match_raw'))
    conn.execute(text('TRUNCATE TABLE stg_player_raw'))
    conn.execute(text('TRUNCATE TABLE stg_player_stats_fbref'))
    conn.execute(text('TRUNCATE TABLE stg_team_raw'))
    conn.commit()
    print('[OK] Staging tables cleared')
"

# Re-run staging load
python -m src.etl.main --staging
```

---

## Troubleshooting

### Issue: FK Constraint Violations (Error 1452)

**Symptom:**
```
(mysql.connector.errors.IntegrityError) 1452 (23000): 
Cannot add or update a child row: a foreign key constraint fails on `epl_dw`.`fact_match`
```

**Solution:**

1. **Verify sentinels exist:**
   ```powershell
   python add_sentinels2.py
   ```

2. **Check which FK is failing:**
   ```powershell
   # Query the error log
   python -c "
   from src.etl.db import get_engine
   from sqlalchemy import text
   
   engine = get_engine()
   with engine.connect() as conn:
       result = conn.execute(text('''
           SELECT player_id FROM dim_player 
           WHERE player_id IN (-1, 6808) 
           LIMIT 5
       '''))
       for row in result:
           print(f'Player: {row}')
   "
   ```

3. **Re-run fact load:**
   ```powershell
   python -m src.etl.main --load-fact-tables
   ```

### Issue: "Can't Connect to MySQL"

**Symptom:**
```
mysql.connector.errors.DatabaseError: Can't connect to MySQL server
```

**Solution:**

```powershell
# 1. Check if container is running
docker ps | findstr epl_mysql

# 2. If not running, start it
docker-compose up -d

# 3. Check container logs
docker-compose logs epl_mysql | tail -20

# 4. Restart container if stuck
docker-compose restart epl_mysql

# 5. Wait 10 seconds and retry
Start-Sleep -Seconds 10
python -m src.etl.main --test-db
```

### Issue: "Table Already Exists" or Schema Errors

**Symptom:**
```
(mysql.connector.errors.DatabaseError) 1050: Table 'dim_player' already exists
```

**Solution:**

```powershell
# Option 1: Restart container (keeps data, re-initializes schema safely)
docker-compose restart epl_mysql

# Option 2: Recreate container (destroys all data)
docker-compose down
docker-compose up -d
```

### Issue: Out of Memory or Slow Performance

**Symptom:**
- Pipeline stalls during fact loading
- MySQL container consuming 100% CPU

**Solution:**

```powershell
# 1. Check Docker resource usage
docker stats epl_mysql

# 2. If memory < 500MB free, close other apps

# 3. Reduce batch size temporarily
# Edit src/etl/load/load_facts.py:
# Change: chunksize = 250
# To:     chunksize = 100

# 4. Run pipeline again
python -m src.etl.main --load-fact-tables
```

### Issue: ETL Hangs or Takes Forever

**Symptom:**
- Pipeline running for > 30 minutes
- No output for several minutes

**Solution:**

```powershell
# 1. Check if process is alive
Get-Process python

# 2. If hung, force stop and check logs
Stop-Process -Name python -Force

# 3. Check last ETL log entry
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT stage, status, MAX(timestamp) 
        FROM etl_log 
        GROUP BY stage, status 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''')).fetchall()
    for row in result:
        print(row)
"

# 4. Restart and try again
python -m src.etl.main --test-db
python -m src.etl.main --full-etl
```

---

## Backup & Recovery

### Manual Database Backup

```powershell
# Create backup directory
mkdir backups
cd backups

# Dump entire database
docker exec epl_mysql mysqldump -u root -p1234 epl_dw > epl_dw_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Verify backup size
Get-ChildItem -Path .\epl_dw_backup_*.sql | Select-Object Name, Length
```

### Restore from Backup

```powershell
# List backups
dir backups\epl_dw_backup_*.sql

# Restore specific backup
docker exec -i epl_mysql mysql -u root -p1234 epl_dw < backups\epl_dw_backup_20251027_120000.sql

# Verify restore
python check_sentinels_and_counts.py
```

### Docker Volume Backup

```powershell
# Backup entire MySQL data volume
docker run --rm -v epl_dwh_mysql_data:/data -v ${PWD}/backups:/backup alpine tar czf /backup/mysql_data_$(Get-Date -Format 'yyyyMMdd').tar.gz -C /data .

# Restore from volume backup
docker volume rm epl_dwh_mysql_data
docker run --rm -v epl_dwh_mysql_data:/data -v ${PWD}/backups:/backup alpine tar xzf /backup/mysql_data_20251027.tar.gz -C /data
```

---

## Performance Monitoring

### Query Execution Times

```powershell
# Check last ETL execution summary
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT 
            stage,
            status,
            MIN(start_time) as start,
            MAX(end_time) as end,
            TIMESTAMPDIFF(SECOND, MIN(start_time), MAX(end_time)) as duration_sec
        FROM etl_log
        GROUP BY stage, status
        ORDER BY start DESC
        LIMIT 10
    ''')).fetchall()
    
    print(f'{'Stage':<20} {'Status':<15} {'Duration (sec)':<20}')
    print('-' * 55)
    for row in result:
        print(f'{row[0]:<20} {row[1]:<15} {row[4]:<20}')
"
```

### Table Size Analysis

```powershell
python -c "
from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'epl_dw'
        ORDER BY data_length DESC
    ''')).fetchall()
    
    print(f'{'Table Name':<25} {'Row Count':<15} {'Size (MB)':<15}')
    print('-' * 55)
    for table, rows, size in result:
        print(f'{table:<25} {rows:<15} {size:<15}')
"
```

### Index Usage

```powershell
# Check if indexes are being used
docker exec epl_mysql mysql -u root -p1234 epl_dw -e "
SELECT object_schema, object_name, count_read, count_write 
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'epl_dw'
ORDER BY count_read DESC
LIMIT 10;
"
```

---

## Best Practices

### ✅ DO:
- Run `truncate.py` to clean data while preserving sentinels
- Run `add_sentinels2.py` before fact loading
- Monitor with `check_sentinels_and_counts.py` after ETL
- Backup before running reset procedures
- Use `--test-db` to verify connectivity before long operations

### ❌ DON'T:
- Manually truncate `dim_player` or `dim_team` (use `truncate.py`)
- Delete sentinel records (-1, 6808)
- Run multiple ETL processes simultaneously
- Stop the Docker container during active fact loading
- Run direct MySQL updates without backing up first

---

## Quick Reference

| Task | Command |
|------|---------|
| Start database | `docker-compose up -d` |
| Stop database | `docker-compose down` |
| Full pipeline | `python -m src.etl.main --full-etl && python -m src.etl.main --load-fact-tables` |
| Reset data | `python truncate.py && python add_sentinels2.py` |
| Check status | `python check_sentinels_and_counts.py` |
| Verify sentinels | `python add_sentinels2.py` |
| Backup database | `docker exec epl_mysql mysqldump -u root -p1234 epl_dw > backup.sql` |
| Test connection | `python -m src.etl.main --test-db` |

---

## Support & Contact

For issues or questions:
1. Check the [README.md](README.md) for general info
2. Consult [ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md) for detailed process
3. Review logs in terminal output
4. Run troubleshooting commands above

**Last tested:** October 27, 2025  
**Python version:** 3.13  
**MySQL version:** 8.0  
**Docker Desktop:** Latest
