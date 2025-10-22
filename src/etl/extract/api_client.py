"""ETL API client for football-data.org.
Provides functions to fetch data from the football-data.org API
"""
import requests
import datetime as datetime
import pandas as pd
import sqlalchemy
import pathlib
import json
from ..db import get_engine
from sqlalchemy import text


_headers = {
    "X-Auth-Token": "b83c3e7f3f7a43bb8562fc38be616618",
    "Accept": "application/json"
}


def log_api_call(
    api_name: str,
    endpoint: str,
    season: int = None,
    load_start_time: datetime.datetime = None,
    load_end_time: datetime.datetime = None,
    status: str = "IN_PROGRESS",
    rows_processed: int = None,
    error_message: str = None
) -> None:
    """Log or update an API call in ETL_Api_Manifest table for audit tracking.
    
    Uses INSERT...ON DUPLICATE KEY UPDATE to maintain a single record per API call.
    This is the standard operational approach: one record per endpoint+season combination.
    
    Args:
        api_name: Name of the API source (e.g., 'football-data.org')
        endpoint: API endpoint called (e.g., '/competitions/PL/teams')
        season: Season year (e.g., 2023)
        load_start_time: Start time of the load operation
        load_end_time: End time of the load operation
        status: Status of the operation ('IN_PROGRESS', 'SUCCESS', 'FAILED')
        rows_processed: Number of rows processed/loaded
        error_message: Error message if status is 'FAILED'
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Use INSERT...ON DUPLICATE KEY UPDATE to upsert the record
            # This ensures we update the same row instead of creating duplicates
            upsert_query = text("""
                INSERT INTO ETL_Api_Manifest 
                (api_name, endpoint, season, load_start_time, load_end_time, 
                 status, rows_processed, error_message)
                VALUES 
                (:api_name, :endpoint, :season, :load_start_time, :load_end_time,
                 :status, :rows_processed, :error_message)
                ON DUPLICATE KEY UPDATE
                    load_end_time = :load_end_time,
                    status = :status,
                    rows_processed = :rows_processed,
                    error_message = :error_message
            """)
            
            start_time = load_start_time or datetime.datetime.now()
            
            conn.execute(upsert_query, {
                "api_name": api_name,
                "endpoint": endpoint,
                "season": season,
                "load_start_time": start_time,
                "load_end_time": load_end_time or start_time,
                "status": status,
                "rows_processed": rows_processed,
                "error_message": error_message
            })
            conn.commit()
            print(f"OK Logged API call: {api_name} {endpoint} season={season} status={status}")
    except Exception as e:
        print(f"ERROR logging API call to manifest: {e}")
        # Don't raise - logging failure shouldn't break the main process



#tl to clean team dataframe

 # Fix partial date values like '2019-12' → '2019-12-01'
def normalize_date(value):
    if pd.isna(value):
        return None
    value = str(value)
    if len(value) == 7:  # 'YYYY-MM'
        return value + "-01"
    elif len(value) == 10:  # 'YYYY-MM-DD'
        return value
    else:
        return None
    

# Fetch team data from API endpoint.
def fetch_team_data(url: str | None = None, params: dict | None = None, timeout: int = 10, season: int | None = None) -> dict:
    """Fetch team data from API endpoint for a specific season.
    
    Args:
        url: API endpoint (e.g., https://api.football-data.org/v4/competitions/PL/teams)
        params: optional query parameters (e.g., {"season": 2024})
        timeout: request timeout in seconds
        season: specific season year (if None, uses current year)

    Returns:
        Parsed JSON response as dict

    Raises:
        requests.exceptions.HTTPError: if response status is 4xx/5xx
    """
    if season is None:
        season = datetime.datetime.now().year
    
    if url is None:
        url = f"https://api.football-data.org/v4/competitions/PL/teams?season={season}"
    
    resp = requests.get(url, headers=_headers, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# Convert JSON response to DataFrame.
def read_json(json_data: dict) -> pd.DataFrame:
    if "teams" not in json_data:
        raise ValueError("JSON data does not contain 'teams' key.")
    # Normalize the nested teams list
    df = pd.json_normalize(json_data['teams'])

    # Convert list columns to JSON strings
    list_cols = ['runningCompetitions', 'squad', 'staff']
    for col in list_cols:
        if col in df.columns:
            # Convert the list object in each row to a JSON string
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
    #replace NaN with None
    df = df.where(pd.notnull(df), None)

    # ignore id from DataFrame if present
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    #write to staging table
    engine = get_engine()
    df.columns = df.columns.str.replace('.', '_')
    df["coach_contract_start"] = df["coach_contract_start"].apply(normalize_date)
    df["coach_contract_until"] = df["coach_contract_until"].apply(normalize_date)
    df["coach_dateOfBirth"] = df["coach_dateOfBirth"].apply(normalize_date)
    df["lastUpdated"] = pd.to_datetime(df["lastUpdated"], errors="coerce")
    df['lastUpdated'] = pd.to_datetime(df['lastUpdated'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    print(df.columns.tolist())


    res = df.to_sql('stg_team_raw', engine, if_exists='append', index=False)
    
    engine.dispose()
        #with engine.begin() as conn:
        #   df.to_sql('stg_team_raw', conn, if_exists='append', index=False)    
    print("Inserted rows:", res)
    return df


def fetch_and_load_team_data_for_years(start_year: int = 2023, end_year: int | None = None) -> None:
    """Fetch team data for a range of years and load all to stg_team_raw table.
    
    Logs each API call and data load operation to ETL_Api_Manifest for audit tracking.
    
    Args:
        start_year: starting season year (default 2023)
        end_year: ending season year (default current year)
    
    Returns:
        None (loads directly to database)
    
    Example:
        fetch_and_load_team_data_for_years(2020, 2025)  # loads teams for 2020-2025 seasons
    """
    if end_year is None:
        end_year = datetime.datetime.now().year
    
    print(f"\nFetching and loading team data for seasons {start_year} to {end_year}...\n")
    
    total_rows_loaded = 0
    successful_years = 0
    failed_years = 0
    
    for year in range(start_year, end_year + 1):
        load_start = datetime.datetime.now()
        endpoint = "/competitions/PL/teams"
        
        try:
            print(f"  Fetching teams for season {year}...")
            
            # Log the start of the API call
            log_api_call(
                api_name="football-data.org",
                endpoint=endpoint,
                season=year,
                load_start_time=load_start,
                status="IN_PROGRESS"
            )
            
            # Fetch and load data
            teams_json = fetch_team_data(season=year)
            df_year = read_json(teams_json)
            rows_loaded = len(df_year)
            total_rows_loaded += rows_loaded
            successful_years += 1
            
            load_end = datetime.datetime.now()
            
            # Log success
            log_api_call(
                api_name="football-data.org",
                endpoint=endpoint,
                season=year,
                load_start_time=load_start,
                load_end_time=load_end,
                status="SUCCESS",
                rows_processed=rows_loaded
            )
            
            print(f"  OK Loaded {rows_loaded} teams for season {year}")
            
        except Exception as e:
            failed_years += 1
            load_end = datetime.datetime.now()
            error_msg = str(e)
            
            # Log failure
            log_api_call(
                api_name="football-data.org",
                endpoint=endpoint,
                season=year,
                load_start_time=load_start,
                load_end_time=load_end,
                status="FAILED",
                error_message=error_msg
            )
            
            print(f"  ERROR fetching teams for season {year}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Summary: Loaded {total_rows_loaded} total teams")
    print(f"  OK Successful years: {successful_years}")
    print(f"  ERROR Failed years: {failed_years}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Fetch and load team data for multiple seasons (2023-2025)
    fetch_and_load_team_data_for_years(start_year=2023)


