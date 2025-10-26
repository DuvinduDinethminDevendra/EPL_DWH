#!/usr/bin/env python
import mysql.connector

config = {'host': 'localhost', 'user': 'root', 'password': '1234', 'database': 'epl_dw', 'port': 3307}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

print("=" * 80)
print("TRUNCATING TABLES (KEEPING SENTINELS)")
print("=" * 80)

cursor.execute("SET FOREIGN_KEY_CHECKS=0")
conn.commit()

KEEP = {'dim_date', 'dim_match_mapping', 'dim_season', 'dim_team_mapping', 'ETL_Events_Manifest', 'stg_events_raw', 'fact_match_events'}
TRUNCATE = ['dim_team', 'dim_player', 'dim_referee', 'dim_stadium', 'etl_log', 'ETL_Api_Manifest', 'ETL_Excel_Manifest', 'ETL_File_Manifest', 'ETL_Json_Manifest', 'stg_e0_match_raw', 'stg_player_raw', 'stg_player_stats_fbref', 'stg_referee_raw', 'stg_team_raw', 'fact_match', 'fact_player_stats']

for table in TRUNCATE:
    cursor.execute(f"TRUNCATE TABLE {table}")
    conn.commit()
    print(f"[OK] {table}")

cursor.execute("SET FOREIGN_KEY_CHECKS=1")
conn.commit()

print("=" * 80)
print("[SUCCESS] Truncated 16 tables - Sentinels preserved")
print("=" * 80)

cursor.close()
conn.close()
