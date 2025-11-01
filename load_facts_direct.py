#!/usr/bin/env python3
"""
Direct fact table loading script
Bypasses the main.py orchestration to debug fact loading
"""
import mysql.connector

conn = mysql.connector.connect(host='localhost', port=3307, user='root', password='1234', database='epl_dw')
cursor = conn.cursor()

print("="*70)
print("DIRECT FACT TABLE LOADING")
print("="*70)

insert_query = """
INSERT INTO fact_match_events (
        match_id,
        event_type,
        player_id,
        team_id,
        minute,
        extra_time
)
SELECT  fm.match_id,
        se.type,
        COALESCE(dp.player_id, 6808),
        COALESCE(dtm.dim_team_id, -1),
        se.minute,
        CASE WHEN se.statsbomb_period = 2 AND se.minute > 45 THEN se.minute - 45
             WHEN se.statsbomb_period >= 3 THEN se.minute
             ELSE 0 END
FROM    stg_events_raw se
JOIN    dim_match_mapping dmm ON dmm.statsbomb_match_id = se.statsbomb_match_id
INNER JOIN fact_match fm ON fm.match_id = dmm.csv_match_id
LEFT JOIN dim_team_mapping dtm ON dtm.statsbomb_team_id = se.team_id
LEFT JOIN dim_player dp ON dp.player_name = se.player_name
WHERE   se.status = 'LOADED'
  AND   se.minute BETWEEN 0 AND 120
"""

try:
    print("\nInserting events into fact_match_events...")
    cursor.execute(insert_query)
    rows_inserted = cursor.rowcount
    conn.commit()
    print(f"[OK] Inserted {rows_inserted:,} events")
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()

# Verify
cursor.execute("SELECT COUNT(*) FROM fact_match_events")
count = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT match_id) as matches,
           COUNT(DISTINCT player_id) as players,
           COUNT(DISTINCT team_id) as teams
    FROM fact_match_events
""")
details = cursor.fetchone()

print(f"\nFinal Status:")
print(f"  Total events:   {count:>10,}")
print(f"  Unique matches: {details[0]:>10,}")
print(f"  Unique players: {details[1]:>10,}")
print(f"  Unique teams:   {details[2]:>10,}")

cursor.close()
conn.close()

print("\n" + "="*70)
print("SUCCESS! Fact table loaded.")
print("="*70)
