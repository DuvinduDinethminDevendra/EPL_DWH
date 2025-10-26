from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Alter start_time to have a default value
    try:
        conn.execute(text('ALTER TABLE etl_log MODIFY start_time DATETIME DEFAULT CURRENT_TIMESTAMP'))
        conn.commit()
        print("[OK] Updated etl_log.start_time to have DEFAULT CURRENT_TIMESTAMP")
    except Exception as e:
        print(f"[ERROR] {str(e)[:100]}")
