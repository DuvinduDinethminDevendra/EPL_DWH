from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT log_id, job_name, phase_step, status, 
               TIMESTAMPDIFF(SECOND, start_time, end_time) as duration_sec, 
               message 
        FROM etl_log 
        WHERE job_name LIKE 'load_fact_tables%'
        ORDER BY log_id DESC 
        LIMIT 15
    """))
    
    print("\n" + "="*100)
    print("ETL_LOG ENTRIES FOR load_fact_tables")
    print("="*100 + "\n")
    
    for row in result.fetchall():
        log_id, job, phase, status, duration, msg = row
        print(f"[{log_id}] {job} → {phase}")
        print(f"    Status: {status} | Duration: {duration}s")
        print(f"    Message: {msg}\n")
    
    # Count final results
    result2 = conn.execute(text("""
        SELECT COUNT(*) FROM fact_match_events
    """))
    event_count = result2.scalar()
    
    print("="*100)
    print(f"✅ Final Event Count: {event_count:,}")
    print("="*100)
