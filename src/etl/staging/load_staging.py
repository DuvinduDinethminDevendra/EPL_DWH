"""Functions to write staging tables."""
from pathlib import Path
from ..extract.csv_reader import read_csv
from importlib_metadata import files
from ..db import get_engine
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


def write_staging_from_csv():
    _table_name = "stg_e0_match_raw"
    _log_table_name = "ETL_File_Manifest"
    csv_files = list_csv_files(_csvPath)
    number_of_files = len(csv_files)
    engine = get_engine()
    for f in csv_files:
        # write each CSV to the same staging table, appending if it exists
        """ds = pd.DataFrame()
        ds["file_name"] = f
        ds["load_start_time"] = s_time
        ds["load_end_time"] = None
        ds["rows_processed"] = 0
        ds["error_message"] = None
        ds["status"] = "started"
        ds["league_div"] = df['Div'].iloc[0] if 'Div' in df.columns else None """
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

    return True


def write_staging(df, table_name, if_exists="replace"):
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return True

# test run for this file

if __name__ == "__main__":
    write_staging_from_csv()