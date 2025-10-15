
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging
from .config import RAW_DATA_DIR
from pathlib import Path

def run_demo(csv_path):
    import pandas as pd
    df = csv_reader.read_csv(csv_path)
    df = clean.clean_player_names(df)
    print(df.head())

def main():
    parser = argparse.ArgumentParser(description="Run simple ETL demo")
    parser.add_argument("csv", nargs="?", help="Path to a sample CSV file")
    parser.add_argument("--csv", "-c", dest="csv_flag", help="Path to a sample CSV file (alternative flag)")
    args = parser.parse_args()
    csv_path = args.csv_flag or args.csv or "data/raw/E0.csv"
    run_demo(csv_path)

if __name__ == "__main__":
    main()

