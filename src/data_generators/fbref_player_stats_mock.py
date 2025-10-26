"""
FBRef Player Stats Mock Data Generator

Generates realistic mock player stats CSV files for each EPL season.
Output: data/raw/fbref_player_stats/{season}_player_stats.csv

Usage:
    python src/data_generators/fbref_player_stats_mock.py
"""

import os
import pandas as pd
from pathlib import Path
from random import randint, choice, seed

# Set seed for reproducibility
seed(42)

# EPL Teams
TEAMS = [
    'Manchester City', 'Liverpool', 'Manchester United', 'Chelsea',
    'Arsenal', 'Tottenham', 'Leicester City', 'West Ham',
    'Newcastle', 'Brighton', 'Aston Villa', 'Everton',
    'Fulham', 'Brentford', 'Crystal Palace', 'Wolves',
    'Southampton', 'Nottingham Forest', 'Luton Town', 'Bournemouth',
    'Ipswich Town', 'Burnley', 'Sheffield United', 'Middlesbrough',
]

# Player name templates (repeated across seasons with variations)
BASE_PLAYERS = [
    'De Bruyne', 'Haaland', 'Salah', 'Van Dijk', 'Cancelo',
    'Rodri', 'Dias', 'Nunez', 'Son', 'Kane', 'Saka', 'Martinelli',
    'Shaw', 'Mount', 'Antony', 'Rashford', 'Bruno Fernandes',
    'Zinchenko', 'Ødegaard', 'Rice', 'Declan Rice', 'Palmer', 'Mudryk',
    'Foden', 'Grealish', 'Stones', 'Gvardiol', 'Akanji', 'Gundogan',
    'Alvarez', 'Durán', 'Mateo Kovacic', 'Enzo Fernández', 'Reece James',
    'Tomáš Souček', 'Bukayo Saka', 'Leandro Trossard', 'Gabriel Magalhaes',
    'Romain Grosjean', 'Alexander Isak', 'Jürgen Locadia', 'Ivan Perišić',
]

SEASONS = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']


def generate_season_stats(season: str, num_matches_per_team: int = 30) -> pd.DataFrame:
    """Generate mock player stats for a season."""
    rows = []
    
    for team in TEAMS:
        # 20-25 players per team
        num_players = 22 + len(team) % 4
        
        for i in range(num_players):
            player_name = BASE_PLAYERS[i % len(BASE_PLAYERS)]
            # Add small variation so not exact duplicates across seasons
            if i % 5 == 0:
                player_name = f"{player_name} Jr."
            
            # Vary by team and season
            team_hash = hash(team) % 1000
            season_hash = hash(season) % 1000
            player_hash = hash(player_name + team + season) % 1000
            
            # Minutes played (0-2700, or 0 for unused players)
            if randint(1, 100) <= 70:  # 70% chance player actually played
                minutes_base = 1200 + (player_hash % 1500)
                minutes_played = max(0, minutes_base)
            else:
                minutes_played = 0
            
            # Stats scale with minutes
            minute_factor = minutes_played / 1500.0 if minutes_played > 0 else 0
            
            goals = max(0, int(minute_factor * (5 + (player_hash % 10))) - 2)
            assists = max(0, int(minute_factor * (3 + (player_hash % 8))) - 1)
            shots = max(0, int(minute_factor * (4 + (player_hash % 6))))
            shots_on_target = max(0, int(shots * 0.4))
            yellow_cards = randint(0, 3) if minutes_played > 500 else 0
            red_cards = 1 if randint(1, 100) > 95 and minutes_played > 1000 else 0
            xg = round(minute_factor * (2.5 + (player_hash % 100) / 100.0), 2)
            xa = round(minute_factor * (1.5 + (player_hash % 100) / 100.0), 2)
            
            rows.append({
                'Player': player_name,
                'Squad': team,
                'Min': minutes_played,
                'Gls': goals,
                'Ast': assists,
                'Sh': shots,
                'SoT': shots_on_target,
                'CrdY': yellow_cards,
                'CrdR': red_cards,
                'xG': xg,
                'xA': xa,
                'Season': season,
            })
    
    return pd.DataFrame(rows)


def main():
    """Generate all season CSVs."""
    output_dir = Path("data/raw/fbref_player_stats")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print("GENERATING MOCK FBRef PLAYER STATS")
    print("="*80 + "\n")
    
    total_rows = 0
    
    for season in SEASONS:
        df = generate_season_stats(season)
        
        season_slug = season.replace('-', '_').lower()
        output_file = output_dir / f"{season}_player_stats.csv"
        
        df.to_csv(output_file, index=False)
        
        num_rows = len(df)
        total_rows += num_rows
        
        print(f"✅ Created {output_file.relative_to('.')} ({num_rows:,} rows)")
    
    print("\n" + "="*80)
    print(f"✅ TOTAL: {total_rows:,} mock player stats rows generated")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
