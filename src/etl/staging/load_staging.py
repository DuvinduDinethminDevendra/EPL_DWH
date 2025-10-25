"""Functions to write staging tables."""
from pathlib import Path
from ..extract.csv_reader import read_csv
from ..extract.api_client import fetch_and_load_team_data_for_years
from ..extract.json_reader import JSONReader
from ..extract.excel_reader import load_excel_data
from ..extract.statsbomb_reader import fetch_and_load_statsbomb_events
from importlib_metadata import files
from ..db import get_engine
from sqlalchemy import text
import pandas as pd
import datetime as dateTime



# Create a list of csv files in the data/raw directory (project root -> data/raw)
_csvPath = Path(__file__).resolve().parents[3] / "data" / "raw"
def list_csv_files(directory):
    p = Path(directory)
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")
    files = [str(f) for f in p.rglob("*.csv")]
    return files

# Write staging table from CSV files
def write_staging_from_csv():
    _table_name = "stg_e0_match_raw"
    _log_table_name = "ETL_File_Manifest"
    csv_files = list_csv_files(_csvPath)
    number_of_files = len(csv_files)
    engine = get_engine()
    for f in csv_files:
        check_file_existence_query = f"SELECT COUNT(*) FROM ETL_File_Manifest WHERE file_name = '{Path(f).name}'"
        with engine.connect() as conn:
            result = conn.execute(text(check_file_existence_query))
        file_exists = result.scalar() > 0
        # write each CSV to the same staging table, appending if it exists
        if not file_exists:
            print(f"Processing file {f} ({number_of_files} total files)...")
            file_name = Path(f).name
            load_start = dateTime.datetime.now()
            load_end = None
            status = 'Failure'  # Default to failure until success is confirmed
            rows_processed = 0
            error_msg = None
            league_div = None
            try:
                df = read_csv(f)
                if 'Div' in df.columns and not df.empty:
                    league_div = df['Div'].iloc[0]
                inserted_rows = df.to_sql(_table_name, engine, if_exists="append", index=False)
                rows_processed = inserted_rows if inserted_rows is not None else df.shape[0]
                status = 'Success'

            except Exception as e:
                error_msg = str(e)
            finally:
                load_end = dateTime.datetime.now()
                # Log the ETL process details
                log_df = pd.DataFrame([{
                    "file_name": file_name,
                    "load_start_time": load_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "load_end_time": load_end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    "rows_processed": rows_processed,
                    "error_message": error_msg,
                    "status": status,
                    "league_div": league_div
                }])
                try:
                    log_df.to_sql(_log_table_name, engine, if_exists="append", index=False)
                except Exception as e:
                    print(f"Failed to log end of ETL for file {f}: {e}")
        else:
            # If the file exists in the manifest, skip processing
            print(f"File {f} already processed, skipping.")

    return True

# Write staging table from API data
def write_staging_from_api(start_year: int = 2023, end_year: int = None):
    """Load team data from football-data.org API for multiple seasons."""
    print(f"\nLoading team data from API (football-data.org)...")
    try:
        fetch_and_load_team_data_for_years(start_year=start_year, end_year=end_year)
        print("API data loading completed successfully!")
        return True
    except Exception as e:
        print(f"Error loading API data: {e}")
        return False


# Write staging table from JSON data
def write_staging_from_json():
    """Load player data from JSON files into stg_player_raw."""
    print(f"\nLoading player data from JSON files...")
    try:
        json_dir = Path(__file__).resolve().parents[3] / "data" / "raw" / "json"
        if not json_dir.exists():
            print(f"JSON directory not found: {json_dir}")
            return False
        
        reader = JSONReader(str(json_dir))
        reader.read_json_files()
        print("JSON data loading completed successfully!")
        return True
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return False


def write_staging_from_excel():
    """Load Excel data (referees, stadiums, etc.) from xlsx files."""
    print(f"\nLoading Excel data from xlsx files...")
    try:
        results = load_excel_data()
        if results:
            print(f"Excel data loading completed successfully! Processed {len(results)} files")
            for file_name, (rows, status) in results.items():
                print(f"  {file_name}: {rows} rows - {status}")
            return True
        else:
            print("No Excel files found to process")
            return True  # Return True even if no files, as this is not an error
    except Exception as e:
        print(f"Error loading Excel data: {e}")
        return False


def write_staging(df, table_name, if_exists="replace"):
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return True


def load_dim_player():
    """Load distinct players from stg_player_raw into dim_player dimension table."""
    print("\nLoading player dimension from staging table...")
    try:
        engine = get_engine()
        
        # SQL to insert distinct players with ON DUPLICATE KEY UPDATE
        sql = """
        INSERT INTO dim_player (player_name, created_at)
        SELECT DISTINCT player_name, NOW()
        FROM stg_player_raw
        WHERE player_name IS NOT NULL
        ON DUPLICATE KEY UPDATE
            created_at = VALUES(created_at);
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            conn.commit()
            rows_affected = result.rowcount
        
        print(f"Loaded {rows_affected} distinct players into dim_player")
        return True
    except Exception as e:
        print(f"Error loading dim_player: {e}")
        return False


def load_all_staging():
    """Master orchestration function - load all staging tables from all sources."""
    print("\n" + "="*70)
    print("ETL STAGING LOAD - UNIFIED ORCHESTRATION")
    print("="*70)
    
    results = {}
    
    # Load JSON data (players)
    results['json'] = write_staging_from_json()
    
    # Load API data (teams)
    results['api'] = write_staging_from_api()
    
    # Load StatsBomb events
    results['statsbomb'] = fetch_and_load_statsbomb_events()
    
    # Load CSV data (matches)
    results['csv'] = write_staging_from_csv()
    
    # Load Excel data (referees, stadiums, etc.)
    results['excel'] = write_staging_from_excel()
    
    # Print summary
    print("\n" + "="*70)
    print("ETL STAGING LOAD SUMMARY")
    print("="*70)
    print(f"JSON (Players): {'SUCCESS' if results['json'] else 'FAILED'}")
    print(f"API (Teams): {'SUCCESS' if results['api'] else 'FAILED'}")
    print(f"StatsBomb (Events): {'SUCCESS' if results['statsbomb'] else 'FAILED'}")
    print(f"CSV (Matches): {'SUCCESS' if results['csv'] else 'FAILED'}")
    print(f"Excel (Referees/Stadiums): {'SUCCESS' if results['excel'] else 'FAILED'}")
    print("="*70 + "\n")
    
    return all(results.values())


# test run for this file

if __name__ == "__main__":
    load_all_staging()