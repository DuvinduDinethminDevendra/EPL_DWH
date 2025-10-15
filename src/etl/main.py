"""Simple ETL runner for development/demo purposes."""
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging


def run_demo(csv_path):
    import pandas as pd
    df = csv_reader.read_csv(csv_path)
    df = clean.clean_player_names(df)
    print(df.head())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run simple ETL demo")
    parser.add_argument("csv", help="Path to a sample CSV file")
    args = parser.parse_args()
    run_demo(args.csv)
