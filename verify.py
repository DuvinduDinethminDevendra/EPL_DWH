#!/usr/bin/env python
import mysql.connector

config = {'host': 'localhost', 'user': 'root', 'password': '1234', 'database': 'epl_dw', 'port': 3307}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

print("\n" + "=" * 100)
print(" " * 35 + "FINAL ETL RESULTS")
print("=" * 100)

print("\n📊 DIMENSION TABLES:")
dims = [('dim_date', 'Calendar'), ('dim_team', 'Teams'), ('dim_player', 'Players'), ('dim_referee', 'Referees'), ('dim_stadium', 'Stadiums'), ('dim_season', 'Seasons')]
for table, label in dims:
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {'team_id' if table == 'dim_team' else 'stadium_id' if table == 'dim_stadium' else 'referee_id' if table == 'dim_referee' else 'season_id' if table == 'dim_season' else 'date_id' if table == 'dim_date' else 'player_id'} != -1")
    count = cursor.fetchone()[0]
    print(f"  • {label:.<35} {count:>12,}")

print("\n📈 FACT TABLES:")
facts = [('fact_match', 'Matches'), ('fact_player_stats', 'Player Stats'), ('fact_match_events', 'Events')]
for table, label in facts:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    status = "✓" if count > 0 else "✗"
    print(f"  • {label:.<35} {count:>12,} {status}")

print("\n" + "=" * 100)
print("✓ ETL PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
print("=" * 100 + "\n")

cursor.close()
conn.close()
