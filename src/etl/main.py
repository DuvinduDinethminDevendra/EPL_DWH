
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging
from .config import RAW_DATA_DIR
from pathlib import Path
from .db import get_engine
from sqlalchemy import text

def run_demo(csv_path):
    import pandas as pd
    df = csv_reader.read_csv(csv_path)
    df = clean.clean_player_names(df)
    print(df.head())

def main():
    parser = argparse.ArgumentParser(description="Run simple ETL demo")
    parser.add_argument("csv", nargs="?", help="Path to a sample CSV file")
    parser.add_argument("--csv", "-c", dest="csv_flag", help="Path to a sample CSV file (alternative flag)")
    parser.add_argument("--test-db", action="store_true", help="Run a quick DB connectivity test and print the result")
    args = parser.parse_args()
    csv_path = args.csv_flag or args.csv or "data/raw/E0.csv"
    if args.test_db:
        run_db_test()
    else:
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

