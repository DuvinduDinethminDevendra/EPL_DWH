
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging
from .load_warehouse import run_complete_etl_pipeline
from .config import RAW_DATA_DIR
from pathlib import Path
from .db import get_engine
from sqlalchemy import text

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

def main():
    parser = argparse.ArgumentParser(description="EPL DWH ETL Pipeline")
    parser.add_argument("csv", nargs="?", help="Path to a sample CSV file (for demo mode)")
    parser.add_argument("--csv", "-c", dest="csv_flag", help="Path to a sample CSV file (alternative flag)")
    parser.add_argument("--test-db", action="store_true", help="Run a quick DB connectivity test")
    parser.add_argument("--full-etl", action="store_true", help="Run the complete ETL pipeline")
    parser.add_argument("--staging", action="store_true", help="Run only the staging load")
    parser.add_argument("--warehouse", action="store_true", help="Run only the warehouse load")
    
    args = parser.parse_args()
    csv_path = Path(__file__).parent.parent.parent.parent / "EPL_DWH" / "data" / "raw" / "csv" / "E0Season_20252026.csv"
    
    if args.test_db:
        run_db_test()
    elif args.full_etl:
        run_full_etl_pipeline()
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
