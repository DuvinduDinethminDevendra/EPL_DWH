from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    # Rebuild mapping with v2 script
    with open('src/sql/rebuild_match_mapping_v2.sql', 'r') as f:
        sql = f.read()
    
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    for i, stmt in enumerate(statements):
        try:
            result = conn.execute(text(stmt))
            conn.commit()
            
            if stmt.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                if rows:
                    print(f"[{i}] Query result:")
                    for row in rows:
                        print(f"  {row}")
            else:
                print(f"[{i}] [OK] Executed")
        except Exception as e:
            print(f"[{i}] [ERROR] {str(e)[:100]}")
            conn.rollback()

print("\n[OK] Match mapping rebuilt")
