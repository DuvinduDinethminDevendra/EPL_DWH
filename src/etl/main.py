
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging
from .load_warehouse import run_complete_etl_pipeline
from .config import RAW_DATA_DIR
from pathlib import Path
from .db import get_engine
from sqlalchemy import text
import subprocess
import os
from tqdm import tqdm
from datetime import datetime

def run_demo(csv_path):
    import pandas as pd
    df = csv_reader.read_csv(csv_path)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", 5)
    pd.set_option("display.width", 200)
    print(df)       

def run_full_etl_pipeline():
    """Run the complete ETL pipeline: Staging -> Dimensions -> Facts"""
    print("\n" + "="*80)
    print("RUNNING COMPLETE EPL DWH ETL PIPELINE")
    print("="*80)
    
    try:
        # Run complete pipeline (handles staging, cleaning, and dimension loads)
        run_complete_etl_pipeline()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] ETL pipeline failed: {str(e)}")
        return False

def load_fact_tables():
    """Load fact tables using optimized SQL scripts with progress bar and logging"""
    print("\n" + "="*80)
    print("LOADING FACT TABLES FROM STAGING DATA")
    print("="*80)
    
    # Get SQL directory path (src/sql)
    sql_dir = Path(__file__).parent.parent / "sql"
    engine = get_engine()
    
    # Scripts to run in order (includes load_fact_match as step 1!)
    scripts = [
        ("load_fact_match.sql", "Load fact_match from CSV (830 matches)"),
        ("load_fact_match_events_step1.sql", "Step 1: Create temporary aggregation table"),
        ("load_fact_match_events_step2.sql", "Step 2: Verify match mappings"),
        ("load_fact_match_events_step3_final.sql", "Step 3: Load 1.36M events into fact_match_events"),
        ("load_fact_match_events_step4_verify.sql", "Step 4: Verify loaded data"),
        ("final_row_count.sql", "Final verification: Show all table row counts"),
    ]
    
    # Log start to ETL_Log
    start_time = datetime.now()
    try:
        with engine.connect() as conn:
            log_query = text("""
                INSERT INTO etl_log (job_name, phase_step, status, start_time, message)
                VALUES (:job, :phase, :stat, :start, :msg)
            """)
            conn.execute(log_query, {
                "job": "load_fact_tables",
                "phase": "initialization",
                "stat": "STARTED",
                "start": start_time,
                "msg": f"Starting fact table load with {len(scripts)} scripts"
            })
            conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log to ETL_Log: {str(e)}")
    
    # Progress bar for overall scripts
    print("\nExecuting SQL scripts with progress:\n")
    
    try:
        for idx, (script_name, description) in enumerate(tqdm(scripts, desc="Overall Progress", unit="script"), 1):
            script_path = sql_dir / script_name
            step_start = datetime.now()
            
            if not script_path.exists():
                print(f"\n❌ [WARNING] Script not found: {script_path}")
                continue
            
            print(f"\n  ▶ [{idx}/{len(scripts)}] {description}")
            
            # Read SQL file
            with open(script_path, 'r') as f:
                sql_content = f.read()
            
            # Execute statements
            try:
                with engine.connect() as conn:
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    
                    # Progress bar for statements in this script
                    for statement in tqdm(statements, desc=f"    {script_name}", leave=False, unit="stmt"):
                        try:
                            result = conn.execute(text(statement))
                            conn.commit()
                            
                            # Print results if SELECT
                            if statement.strip().upper().startswith("SELECT"):
                                rows = result.fetchall()
                                if rows:
                                    for row in rows[:5]:  # Limit output
                                        print(f"    → {row}")
                                    if len(rows) > 5:
                                        print(f"    ... and {len(rows)-5} more rows")
                        except Exception as e:
                            print(f"\n  ❌ [ERROR] {str(e)}")
                            conn.rollback()
                            # Log failure
                            try:
                                with engine.connect() as log_conn:
                                    log_conn.execute(text("""
                                        INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                                        VALUES (:job, :phase, :stat, :end, :msg)
                                    """), {
                                        "job": "load_fact_tables",
                                        "phase": script_name,
                                        "stat": "FAILED",
                                        "end": datetime.now(),
                                        "msg": f"Failed: {str(e)}"
                                    })
                                    log_conn.commit()
                            except:
                                pass
                            return False
                
                # Log successful completion of this step
                step_end = datetime.now()
                step_duration = (step_end - step_start).total_seconds()
                try:
                    with engine.connect() as log_conn:
                        log_conn.execute(text("""
                            INSERT INTO etl_log (job_name, phase_step, status, start_time, end_time, message)
                            VALUES (:job, :phase, :stat, :start, :end, :msg)
                        """), {
                            "job": "load_fact_tables",
                            "phase": script_name,
                            "stat": "COMPLETED",
                            "start": step_start,
                            "end": step_end,
                            "msg": f"✓ {description} ({step_duration:.2f}s)"
                        })
                        log_conn.commit()
                except Exception as e:
                    print(f"[WARNING] Could not log step completion: {str(e)}")
                    
            except Exception as e:
                print(f"\n  ❌ [ERROR] Step failed: {str(e)}")
                return False
        
        # Log completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "load_fact_tables",
                    "phase": "completion",
                    "stat": "COMPLETED",
                    "end": end_time,
                    "msg": f"All fact tables loaded successfully in {duration:.2f} seconds"
                })
                conn.commit()
        except Exception as e:
            print(f"[WARNING] Could not log completion: {str(e)}")
        
        print("\n" + "="*80)
        print(f"✅ FACT TABLE LOADING COMPLETED SUCCESSFULLY ({duration:.2f}s)")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fact table loading failed: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="EPL DWH ETL Pipeline")
    parser.add_argument("csv", nargs="?", help="Path to a sample CSV file (for demo mode)")
    parser.add_argument("--csv", "-c", dest="csv_flag", help="Path to a sample CSV file (alternative flag)")
    parser.add_argument("--test-db", action="store_true", help="Run a quick DB connectivity test")
    parser.add_argument("--full-etl", action="store_true", help="Run the complete ETL pipeline (staging + dimensions)")
    parser.add_argument("--staging", action="store_true", help="Run only the staging load")
    parser.add_argument("--warehouse", action="store_true", help="Run only the warehouse load (dimensions)")
    parser.add_argument("--load-fact-tables", action="store_true", help="Load fact tables from staging data (run after --full-etl)")
    
    args = parser.parse_args()
    csv_path = Path(__file__).parent.parent.parent.parent / "EPL_DWH" / "data" / "raw" / "csv" / "E0Season_20252026.csv"
    
    if args.test_db:
        run_db_test()
    elif args.full_etl:
        run_full_etl_pipeline()
    elif args.load_fact_tables:
        load_fact_tables()
    elif args.staging:
        print("\nRunning staging load only...")
        load_staging.load_all_staging()
    elif args.warehouse:
        print("\nRunning complete warehouse pipeline (includes staging, cleaning, and dimensions)...")
        run_complete_etl_pipeline()
    else:
        # Default demo mode
        run_demo(csv_path)


def run_db_test():
    """Connect to the configured database, run a simple test query, and print output."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # run a simple SELECT to verify connectivity and show server version
            r1 = conn.execute(text("SELECT 1 AS ok"))
            ok = r1.fetchone()
            r2 = conn.execute(text("SELECT VERSION() AS version"))
            ver = r2.fetchone()
            print("DB connectivity test result:")
            print("SELECT 1 ->", ok[0] if ok is not None else None)
            print("VERSION ->", ver[0] if ver is not None else None)
    except Exception as e:
        print("DB connectivity test failed:", str(e))

if __name__ == "__main__":
    main()
