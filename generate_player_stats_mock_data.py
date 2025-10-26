#!/usr/bin/env python3
"""
Generate valid player stats mock data with real EPL team and player names
Run this BEFORE --load-player-stats to ensure the staging table has valid data
"""

from src.etl.db import get_engine
from sqlalchemy import text

# Real EPL teams
TEAMS = [
    'Arsenal FC', 'Aston Villa FC', 'Brentford FC', 'Brighton & Hove Albion FC',
    'Burnley FC', 'Chelsea FC', 'Crystal Palace FC', 'Everton FC', 'Fulham FC',
    'Ipswich Town FC', 'Leeds United FC', 'Leicester City FC', 'Liverpool FC',
    'Luton Town FC', 'Manchester City FC', 'Manchester United FC', 'Newcastle United FC',
    'Nottingham Forest FC', 'Sheffield United FC', 'Southampton FC', 'Sunderland AFC',
    'Tottenham Hotspur FC', 'West Ham United FC', 'Wolverhampton Wanderers FC', 'AFC Bournemouth'
]

# Real players by team
PLAYERS_BY_TEAM = {
    'Arsenal FC': ['Saka', 'Odegaard', 'Martinelli', 'Partey', 'White', 'Zinchenko', 'Jesus', 'Trossard'],
    'Manchester City FC': ['De Bruyne', 'Haaland', 'Cancelo', 'Rodri', 'Dias', 'Grealish', 'Alvarez', 'Foden'],
    'Liverpool FC': ['Salah', 'Van Dijk', 'Alisson', 'Henderson', 'Mane', 'Nunez', 'Trent', 'Fabinho'],
    'Chelsea FC': ['Sterling', 'Pereira', 'James', 'Mount', 'Gallagher', 'Enzo', 'Mudryk', 'Madueke'],
    'Manchester United FC': ['Bruno', 'Martial', 'Rashford', 'McTominay', 'Casemiro', 'Shaw', 'Varane', 'Dalot'],
    'Newcastle United FC': ['Isak', 'Joelinton', 'Trippier', 'Guimaraes', 'Botman', 'Targett', 'Almiron', 'Tonali'],
    'Brighton & Hove Albion FC': ['Mwepu', 'Caicedo', 'Tadic', 'Welbeck', 'Veltman', 'Webster', 'Lamptey', 'Jahanbakhsh'],
    'Brentford FC': ['Mbeumo', 'Toney', 'Ajer', 'Dasilva', 'Hickey', 'Jensen', 'Simons', 'Sorensen'],
    'Tottenham Hotspur FC': ['Son', 'Kane', 'Richarlison', 'Kulusevski', 'Porro', 'Romero', 'Van de Ven', 'Sarr'],
    'Crystal Palace FC': ['Olise', 'Zaha', 'Guehi', 'Eze', 'Nketiah', 'Mitchell', 'Andersen', 'Ward'],
    'Everton FC': ['Iwobi', 'Gordon', 'Doucoure', 'Harrison', 'Coady', 'Holgate', 'Coleman', 'Vinagre'],
    'West Ham United FC': ['Rice', 'Ings', 'Soucek', 'Bowen', 'Antonio', 'Zouma', 'Coufal', 'Emerson'],
    'Fulham FC': ['Pereira', 'Adarabioyo', 'Solomon', 'Palhinha', 'Willian', 'Ream', 'De Cordova', 'Tielemans'],
    'Wolverhampton Wanderers FC': ['Neves', 'Cunha', 'Lemina', 'Aït Nouri', 'Coady', 'Kilman', 'Semedo', 'Sa'],
    'Nottingham Forest FC': ['Awoniyi', 'Hudson-Odoi', 'Wood', 'Yates', 'Murillo', 'Niakhate', 'Williams', 'Laryea'],
    'AFC Bournemouth': ['Solanke', 'Lerma', 'Mepham', 'Cook', 'Tavernier', 'Brady', 'Evanson', 'Senesi'],
    'Aston Villa FC': ['Watkins', 'Buendia', 'McGinn', 'Coutinho', 'Martinez', 'Konsa', 'Cash', 'Ramsey'],
    'Southampton FC': ['Salisu', 'Walker-Peters', 'Valery', 'Ward-Prowse', 'Aribo', 'Armstrong', 'Sulemana', 'Livramento'],
    'Leicester City FC': ['Maddison', 'Vardy', 'Mendy', 'Ndidi', 'Castagne', 'Soyuncu', 'Pereira', 'Tielemans'],
    'Ipswich Town FC': ['Delap', 'Cresswell', 'Johnson', 'Jackson', 'Lamy', 'Davis', 'Azaz', 'Woolfenden'],
    'Leeds United FC': ['Sinisterra', 'Ayling', 'Piroe', 'Struijk', 'Rodon', 'Byram', 'Adams', 'Gnonto'],
    'Burnley FC': ['Cornet', 'Amdouni', 'Vitinha', 'Brownhill', 'Barnes', 'Iling', 'Edmundson', 'Roberts'],
    'Luton Town FC': ['Adebayo', 'Dewsbury-Hall', 'Clark', 'Lockyer', 'Ogbene', 'Osho', 'Kaminski', 'Kabore'],
    'Sheffield United FC': ['Heck', 'Gibbs-White', 'Anel', 'Lowe', 'Baldock', 'Stevens', 'Norwood', 'Robinson'],
    'Sunderland AFC': ['Maguire', 'Stewart', 'Embalo', 'Ba', 'Cirkin', 'Heeley', "O'Nien", 'Alves'],
}

def populate_player_stats_staging():
    """Generate and insert valid player stats mock data"""
    engine = get_engine()
    
    print("Generating valid player stats mock data...")
    
    with engine.connect() as conn:
        # Clear existing data
        conn.execute(text('DELETE FROM stg_player_stats_fbref'))
        
        row_count = 0
        for team_name, player_list in PLAYERS_BY_TEAM.items():
            for season_year in range(2017, 2025):
                season = f'{season_year}-{season_year+1}'
                for idx, player_name in enumerate(player_list):
                    conn.execute(text('''
                        INSERT INTO stg_player_stats_fbref 
                        (player_name, team_name, minutes_played, goals, assists, xg, xa, 
                         yellow_cards, red_cards, shots, shots_on_target, season_label)
                        VALUES (:pname, :tname, :mins, :goals, :assists, :xg, :xa, :yc, :rc, :shots, :sot, :season)
                    '''), {
                        'pname': player_name,
                        'tname': team_name,
                        'mins': 2000 + (idx * 150),
                        'goals': (idx + 1) % 20,
                        'assists': (idx + 1) % 10,
                        'xg': float(2 + (idx % 15)),
                        'xa': float((idx % 8)),
                        'yc': idx % 3,
                        'rc': 0,
                        'shots': 3 + (idx % 10),
                        'sot': 1 + (idx % 5),
                        'season': season
                    })
                    row_count += 1
        
        conn.commit()
        
        result = conn.execute(text('SELECT COUNT(*) FROM stg_player_stats_fbref'))
        total = result.scalar()
        
        print(f"✓ Successfully generated {row_count} player stats records")
        print(f"✓ Total in staging table: {total}")
        return True

if __name__ == '__main__':
    try:
        populate_player_stats_staging()
        print("\n✓ Ready to run: python -m src.etl.main --load-player-stats")
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)
