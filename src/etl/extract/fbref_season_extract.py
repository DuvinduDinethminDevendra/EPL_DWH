"""
FBref season player stats extractor

Usage:
  Extract 'Player Standard Stats' table from an FBref season page.
  - Set environment variables: DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
  - Set FBREF_URL and FBREF_SEASON for the season URL and label
  - Or: export FBREF_LOCAL_HTML to use a local downloaded HTML file (for testing or FBref blocks)
  - Run: python -m src.etl.extract.fbref_season_extract

Example:
  $env:DB_HOST='127.0.0.1'
  $env:DB_PORT='3307'
  $env:DB_USER='root'
  $env:DB_PASS='1234'
  $env:DB_NAME='epl_dw'
  $env:FBREF_URL='https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats'
  $env:FBREF_SEASON='2022/2023'
  python -m src.etl.extract.fbref_season_extract
"""
import os
import re
import logging
from time import sleep
from io import StringIO
import pandas as pd
import requests
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger('fbref_extract')

# DB connection from env with sensible defaults for local dev
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3307'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '1234')
DB_NAME = os.getenv('DB_NAME', 'epl_dw')

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Expected FBref columns that map to our schema
FBREF_TO_DB_COLS = {
    'Player': 'player_name',
    'Squad': 'team_name',
    'Min': 'minutes_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'xG': 'xg',
    'xA': 'xa',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'Sh': 'shots',
    'SoT': 'shots_on_target',
}


def _clean_numeric(val):
    """Convert string numeric (possibly with commas) to int/float or None."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return val
    # remove commas and non-numeric chars except dot and minus
    s = str(val).strip()
    s = re.sub(r'[^0-9.\-]', '', s)
    if not s or s == '-':
        return None
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except (ValueError, TypeError):
        return None


def extract_season(season_url: str, season_name: str, to_sql: bool = True) -> pd.DataFrame:
    """
    Extract player stats table from FBref season page.
    
    Args:
        season_url: URL to the FBref season page
        season_name: Season label (e.g., '2022/2023')
        to_sql: Whether to write extracted data to DB
    
    Returns:
        DataFrame with cleaned and mapped columns ready for DB insert
    """
    log.info(f'Extracting {season_name} from {season_url}')

    html = None
    
    # Try downloading from URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://google.com/',
        'Connection': 'keep-alive',
    }

    for attempt in range(1, 4):
        try:
            log.info(f'Attempt {attempt}: Downloading FBref page...')
            resp = requests.get(season_url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text
            log.info('Successfully downloaded FBref page')
            break
        except requests.exceptions.HTTPError as he:
            log.warning(f'HTTP {resp.status_code} error on attempt {attempt}: {he}')
            if resp.status_code == 403:
                log.warning('FBref returned 403 Forbidden; bot protection detected')
                break
            sleep(attempt * 2)
        except Exception as e:
            log.warning(f'Request error on attempt {attempt}: {e}')
            sleep(attempt * 2)

    # Fallback to local HTML file if download failed
    if not html:
        local_path = os.getenv('FBREF_LOCAL_HTML')
        if local_path and os.path.exists(local_path):
            log.info(f'Using local HTML file: {local_path}')
            with open(local_path, 'r', encoding='utf-8') as fh:
                html = fh.read()
        else:
            raise RuntimeError(
                'Failed to download FBref page and no local HTML provided. '
                'Set FBREF_LOCAL_HTML env var to point to a saved HTML file, or ensure FBref is accessible.'
            )

    # Parse HTML tables
    dfs = pd.read_html(StringIO(html), header=1)
    if not dfs:
        raise RuntimeError('No tables found in HTML')

    df = dfs[0]
    log.info(f'Found table with {len(df)} rows and columns: {list(df.columns)[:5]}...')

    # Normalize column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    # Remove repeated header rows (some pages include headers in body)
    if 'Rk' in df.columns:
        df = df[df['Rk'] != 'Rk']
        log.info(f'Removed header repeats; {len(df)} rows remain')

    # Keep only columns we care about
    available_cols = [c for c in FBREF_TO_DB_COLS.keys() if c in df.columns]
    if not available_cols:
        raise RuntimeError(
            f'None of the expected columns {list(FBREF_TO_DB_COLS.keys())} found in table. '
            f'Found: {list(df.columns)}'
        )

    df = df[available_cols].copy()
    df = df.dropna(subset=['Player'])
    log.info(f'Selected {len(df)} rows with Player info')

    # Rename columns to match DB schema
    df = df.rename(columns=FBREF_TO_DB_COLS)

    # Normalize numeric columns
    numeric_cols = ['minutes_played', 'goals', 'assists', 'yellow_cards', 'red_cards', 'shots', 'shots_on_target']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(_clean_numeric)

    # Numeric but allow decimals
    for col in ['xg', 'xa']:
        if col in df.columns:
            df[col] = df[col].apply(_clean_numeric)

    # Add season label
    df['season_label'] = season_name

    log.info(f'Extracted {len(df)} player records for {season_name}')

    if to_sql:
        log.info('Writing to DB table stg_player_stats_fbref')
        engine = create_engine(DB_URL)
        
        # Append to table (table already exists from schema init)
        try:
            df.to_sql(
                'stg_player_stats_fbref',
                con=engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=100
            )
            log.info(f'Successfully inserted {len(df)} rows into stg_player_stats_fbref')
        except Exception as e:
            log.error(f'Error inserting rows: {e}')
            raise

    return df


if __name__ == '__main__':
    # Example: extract 2022/2023 season
    season_url = os.getenv(
        'FBREF_URL',
        'https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats'
    )
    season_name = os.getenv('FBREF_SEASON', '2022/2023')
    
    try:
        # Run with to_sql=True by default (set to False for dry-run)
        to_sql_flag = os.getenv('FBREF_TO_SQL', 'true').lower() in ('true', '1', 'yes')
        df = extract_season(season_url, season_name, to_sql=to_sql_flag)
        log.info(f'Success! Extracted {len(df)} rows.')
        print(df.head())
    except Exception as e:
        log.error(f'Extraction failed: {e}', exc_info=True)
        exit(1)
