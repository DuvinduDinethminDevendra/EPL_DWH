from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
conn = engine.connect()

# Insert sentinel stadium record
sql = """
INSERT INTO dim_stadium (stadium_id, stadium_name, club, city, country, capacity) 
VALUES (-1, 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 0) 
ON DUPLICATE KEY UPDATE stadium_name = 'UNKNOWN'
"""

try:
    conn.execute(text(sql))
    conn.commit()
    print("[OK] Sentinel stadium record created")
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    conn.close()
