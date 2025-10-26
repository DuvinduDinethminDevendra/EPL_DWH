from src.etl.db import get_engine
from sqlalchemy import text

engine = get_engine()
with open('src/sql/load_fact_player_stats.sql', 'r') as f:
    sql_content = f.read()

statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
print(f"Found {len(statements)} statements\n")

with engine.connect() as conn:
    for i, stmt in enumerate(statements):
        print(f"[{i+1}/{len(statements)}] Executing statement...")
        try:
            result = conn.execute(text(stmt))
            if stmt.strip().upper().startswith('INSERT'):
                print(f"  Rows affected: {result.rowcount}")
            elif stmt.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                for row in rows:
                    print(f"  {row}")
            conn.commit()
        except Exception as e:
            print(f"  ERROR: {str(e)[:150]}")
            conn.rollback()

# Final check
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM fact_player_stats"))
    print(f"\nFinal fact_player_stats count: {result.scalar()}")
