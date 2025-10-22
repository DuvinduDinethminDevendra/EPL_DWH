"""
Generate mock FBref player stats data for testing/demo.

This is useful when FBref is blocking automated downloads.
Run: python -m src.etl.extract.generate_mock_fbref_data
"""
import os
import logging
from datetime import datetime
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger('fbref_mock')

# DB connection from env
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3307'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '1234')
DB_NAME = os.getenv('DB_NAME', 'epl_dw')

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Mock PL team names
TEAMS = [
    'Manchester City', 'Liverpool', 'Manchester United', 'Chelsea',
    'Arsenal', 'Tottenham', 'Leicester City', 'West Ham',
    'Newcastle', 'Brighton', 'Aston Villa', 'Everton',
    'Fulham', 'Brentford', 'Crystal Palace', 'Wolves',
]

# Mock player names (generic examples)
PLAYERS = [
    'De Bruyne', 'Haaland', 'Salah', 'Van Dijk', 'Cancelo',
    'Rodri', 'Dias', 'Nunez', 'Son', 'Kane', 'Saka', 'Martinelli',
    'Shaw', 'Mount', 'Antony', 'Rashford', 'Bruno Fernandes',
    'Zinchenko', 'Ødegaard', 'Rice', 'Declan Rice', 'Palmer', 'Mudryk',
]

SEASONS = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']


def generate_mock_data() -> pd.DataFrame:
    """Generate mock PL player stats across all seasons."""
    rows = []
    
    for season in SEASONS:
        for team in TEAMS:
            # 20-25 players per team per season
            num_players = 22 + len(team) % 4
            for i in range(num_players):
                player_name = f"{PLAYERS[i % len(PLAYERS)]}" if i < len(PLAYERS) else f"Player_{i}"
                
                # Vary stats slightly per season
                minute_base = 1500 + hash((player_name, team, season)) % 1200
                goals = max(0, (hash((player_name, 'goals', season)) % 20) - 5)
                assists = max(0, (hash((player_name, 'assists', season)) % 12) - 3)
                
                rows.append({
                    'player_name': player_name,
                    'team_name': team,
                    'minutes_played': minute_base,
                    'goals': goals,
                    'assists': assists,
                    'xg': round(minute_base / 300 + (hash((player_name, 'xg', season)) % 10) / 10, 2),
                    'xa': round(minute_base / 500 + (hash((player_name, 'xa', season)) % 5) / 10, 2),
                    'yellow_cards': hash((player_name, 'yellow', season)) % 5,
                    'red_cards': 1 if (hash((player_name, 'red', season)) % 20) == 0 else 0,
                    'shots': hash((player_name, 'shots', season)) % 8,
                    'shots_on_target': hash((player_name, 'sot', season)) % 4,
                    'season_label': season,
                    'load_timestamp': datetime.now(),
                })
    
    df = pd.DataFrame(rows)
    log.info(f"Generated {len(df)} mock player records across {len(SEASONS)} seasons")
    return df


def main():
    log.info("Generating mock FBref player stats...")
    
    df = generate_mock_data()
    
    # Connect to DB
    try:
        engine = create_engine(DB_URL, echo=False)
        log.info(f"Connected to DB: {DB_NAME}")
    except Exception as e:
        log.error(f"Failed to connect to DB: {e}")
        return
    
    # Write to staging table
    dry_run = os.getenv('FBREF_DRY_RUN', 'false').lower() == 'true'
    
    if dry_run:
        log.info("DRY RUN: Would insert the following sample rows:")
        print(df.head(10).to_string())
    else:
        try:
            df.to_sql(
                'stg_player_stats_fbref',
                con=engine,
                if_exists='append',
                index=False,
                chunksize=100,
                method='multi',
            )
            log.info(f"✓ Inserted {len(df)} rows into stg_player_stats_fbref")
        except Exception as e:
            log.error(f"Failed to insert rows: {e}")


if __name__ == '__main__':
    main()
