#!/usr/bin/env python
import mysql.connector

config = {'host': 'localhost', 'user': 'root', 'password': '1234', 'database': 'epl_dw', 'port': 3307}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

print("Checking sentinels...")

checks = [
    ("SELECT COUNT(*) FROM dim_stadium WHERE stadium_id = -1", "stadium -1"),
    ("SELECT COUNT(*) FROM dim_team WHERE team_id = -1", "team -1"),
    ("SELECT COUNT(*) FROM dim_player WHERE player_id = -1", "player -1"),
    ("SELECT COUNT(*) FROM dim_player WHERE player_id = 6808", "player 6808"),
    ("SELECT COUNT(*) FROM dim_referee WHERE referee_id = -1", "referee -1"),
]

for sql, label in checks:
    cursor.execute(sql)
    count = cursor.fetchone()[0]
    print(f"  {label}: {count}")

cursor.close()
conn.close()
