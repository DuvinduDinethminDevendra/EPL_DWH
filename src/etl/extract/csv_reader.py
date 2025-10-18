
from logging import Filter
from pathlib import Path
from typing import Union, Optional
import pandas as pd
from ..db import get_engine
from ..config import DATABASE
from sqlalchemy import text


# read_csv function with T-light modifications
def read_csv(path: Union[str, Path], **kwargs) -> pd.DataFrame:
    db_table = "stg_e0_match_raw"
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(p, **kwargs)

    # Normalize column names to lowercase for robust initial handling
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=True)

    # T-light: Define the mapping from normalized CSV names to Target DWH names
    COLUMN_NAME_MAP = {
        'div': 'Div', 'date': 'Date', 'time': 'Time', 'hometeam': 'HomeTeam', 'awayteam': 'AwayTeam', 
        'fthg': 'FTHG', 'ftag': 'FTAG', 'ftr': 'FTR', 'hthg': 'HTHG', 'htag': 'HTAG', 'htr': 'HTR', 
        'referee': 'Referee', 'hs': 'HS', 'as': 'AS', 'hst': 'HST', 'ast': 'AST', 
        'hf': 'HF', 'af': 'AF', 'hc': 'HC', 'ac': 'AC', 'hy': 'HY', 'ay': 'AY', 'hr': 'HR', 'ar': 'AR',
    }
    
    # --- CRITICAL FIX: RENAME COLUMNS ---
    # Create the rename dictionary based only on columns present in the DataFrame
    rename_dict = {
        csv_col: target_col
        for csv_col, target_col in COLUMN_NAME_MAP.items()
        if csv_col in df.columns
    }
    df.rename(columns=rename_dict, inplace=True)
    

    # T-light: Data Type and Key Preparation (Uses the newly renamed columns)
    
    # Convert 'Date' column to datetime (now named 'Date')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce') 
    
    # Ensure all target card columns are present (check for missing source columns)
    for col in ['HY','AY','HR','AR']:
        if col not in df.columns:
            df[col] = None

    # Match Source Key creation (using the new mixed-case column names)
    df['match_source_key'] = (
        df['Date'].astype(str) + "_" +
        df['HomeTeam'].str.replace(" ", "") + "_" +
        df['AwayTeam'].str.replace(" ", "")
    )

    
    # Final Filter and Order
    TARGET_COLS_ORDER = [
        'match_source_key', 'Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 
        'FTHG', 'FTAG', 'FTR', 'HTHG', 'HTAG', 'HTR', 'Referee', 
        'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 
        'HY', 'AY', 'HR', 'AR'
    ]

    # Filter by TARGET_COLS_ORDER (now works because df.columns contains the target names)
    final_cols = [col for col in TARGET_COLS_ORDER if col in df.columns]

    # Check for missing columns in the source that are critical for staging
    for col in TARGET_COLS_ORDER:
        if col not in df.columns:
            print(f"⚠️ Column '{col}' is missing in the source CSV and must be added/derived elsewhere.")


    df = df[final_cols]
    # If requested, query DB for the specified table's column headers and print them
    if db_table:
        try:
            engine = get_engine()
            schema = DATABASE.get('db')
            query = text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table "
                "ORDER BY ORDINAL_POSITION"
            )
            with engine.connect() as conn:
                res = conn.execute(query, {"schema": schema, "table": db_table})
                cols = [row[0] for row in res.fetchall()]
        except Exception as e:
            print(f"Failed to fetch DB headers for table '{db_table}': {e}")

    return df

"""
if __name__ == "__main__":
    # quick local test (won't run in environments without the CSV file)
    sample_csv_path = Path(__file__).resolve().parents[3] / "data" / "raw" / "csv" / "E0Season_20232024.csv"
    try:
        read_csv(sample_csv_path)
    except Exception as e:
        print("Local test failed:", e)"""