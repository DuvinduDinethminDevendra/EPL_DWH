#!/usr/bin/env python
import mysql.connector
config = {'host': 'localhost', 'user': 'root', 'password': '1234', 'database': 'epl_dw', 'port': 3307}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()
print("Adding sentinels...")
#!/usr/bin/env python
"""
Idempotent sentinel inserter for dimension tables.

This script will attempt safe INSERT/ON DUPLICATE patterns for a small set
of sentinel rows used by the ETL (-1 unknown keys, plus player 6808).

It tolerates slightly different column names by trying a few common variants
and ignoring errors if a variant doesn't fit the schema. It is safe to run
multiple times.
"""

import mysql.connector
from mysql.connector import errorcode
import sys

config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'database': 'epl_dw',
    'port': 3307,
    'connect_timeout': 10,
}


def try_statements(cursor, stmts):
    """Try a list of SQL statements until one succeeds (or all fail).
    Returns True if any statement executed successfully or error was duplicate/key exists.
    """
    for sql in stmts:
        try:
            cursor.execute(sql)
            return True
        except mysql.connector.Error as e:
            # Duplicate key or already exists is fine; treat as success
            if e.errno in (errorcode.ER_DUP_ENTRY,):
                return True
            # else try next variant
    return False


def main():
    try:
        conn = mysql.connector.connect(**config)
    except Exception as e:
        print(f"[ERROR] Cannot connect to DB: {e}")
        sys.exit(2)

    cursor = conn.cursor()

    # Each entry is a list of SQL variants to try (most safe -> most specific)
    work = [
        # dim_stadium: try common column names
        ([
            "INSERT INTO dim_stadium (stadium_id, stadium_name, club) VALUES (-1, 'UNKNOWN', 'UNKNOWN') ON DUPLICATE KEY UPDATE stadium_name=stadium_name",
            "INSERT INTO dim_stadium (stadium_id, club) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE club=club",
        ], "dim_stadium"),

        # dim_team
        ([
            "INSERT INTO dim_team (team_id, team_name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE team_name=team_name",
            "INSERT INTO dim_team (team_id, name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE name=name",
        ], "dim_team"),

        # dim_player: insert -1 and 6808
        ([
            "INSERT INTO dim_player (player_id, player_name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE player_name=player_name",
            "INSERT INTO dim_player (player_id, name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE name=name",
        ], "dim_player_-1"),
        ([
            "INSERT INTO dim_player (player_id, player_name) VALUES (6808, 'UNKNOWN') ON DUPLICATE KEY UPDATE player_name=player_name",
            "INSERT INTO dim_player (player_id, name) VALUES (6808, 'UNKNOWN') ON DUPLICATE KEY UPDATE name=name",
        ], "dim_player_6808"),

        # dim_referee
        ([
            "INSERT INTO dim_referee (referee_id, referee_name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE referee_name=referee_name",
            "INSERT INTO dim_referee (referee_id, name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE name=name",
        ], "dim_referee"),

        # dim_season
        ([
            "INSERT INTO dim_season (season_id, season_name) VALUES (-1, 'UNKNOWN') ON DUPLICATE KEY UPDATE season_name=season_name",
        ], "dim_season"),

        # dim_date: try a conservative variant (date_id may be int like YYYYMMDD)
        ([
            "INSERT INTO dim_date (date_id, calendar_date) VALUES (-1, '1970-01-01') ON DUPLICATE KEY UPDATE calendar_date=calendar_date",
            "INSERT INTO dim_date (date_id, date) VALUES (-1, '1970-01-01') ON DUPLICATE KEY UPDATE date=date",
        ], "dim_date"),
    ]

    print("Adding/ensuring sentinel records (idempotent)...")
    for variants, label in work:
        ok = try_statements(cursor, variants)
        if ok:
            try:
                conn.commit()
            except Exception:
                pass
            print(f"[✓] {label}")
        else:
            print(f"[!] {label}: no working SQL variant — check schema")

    cursor.close()
    conn.close()
    print("[SUCCESS] Sentinel upsert complete")


if __name__ == '__main__':
    main()
