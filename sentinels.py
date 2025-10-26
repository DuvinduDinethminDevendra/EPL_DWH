#!/usr/bin/env python
import mysql.connector

config = {'host': 'localhost', 'user': 'root', 'password': '1234', 'database': 'epl_dw', 'port': 3307}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

sentinels = [
    ("INSERT INTO dim_stadium (stadium_id, club) VALUES (-1, 'Unknown Stadium')", "stadium"),
    ("INSERT INTO dim_team (team_id, team_name) VALUES (-1, 'Unknown Team')", "team"),
    ("INSERT INTO dim_player (player_id, player_name) VALUES (-1, 'UNKNOWN')", "player -1"),
    ("INSERT INTO dim_player (player_id, player_name) VALUES (6808, 'UNKNOWN')", "player 6808"),
    ("INSERT INTO dim_referee (referee_id, referee_name) VALUES (-1, 'Unknown Referee')", "referee"),
    ("INSERT INTO dim_season (season_id, season_name) VALUES (-1, 'Unknown Season')", "season"),
]

print("Adding sentinel records...")
for sql, label in sentinels:
    try:
        cursor.execute(sql)
        conn.commit()
        print(f"[✓] {label}")
    except:
        print(f"[✓] {label} (exists)")

cursor.close()
conn.close()
print("[SUCCESS]")
