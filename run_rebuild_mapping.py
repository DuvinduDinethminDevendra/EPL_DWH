from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    # Rebuild mapping
    with open('src/sql/rebuild_match_mapping.sql', 'r') as f:
        sql = f.read()
    
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for stmt in statements:
        try:
            result = conn.execute(text(stmt))
            conn.commit()
            
            if stmt.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                if rows:
                    for row in rows:
                        print(f"{row}")
            else:
                print(f"[OK] Executed: {stmt[:50]}...")
        except Exception as e:
            print(f"[ERROR] {str(e)[:100]}")
            conn.rollback()

print("\n[OK] Match mapping rebuilt")
