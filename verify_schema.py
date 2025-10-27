import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='1234',
        database='epl_dw'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = "epl_dw"')
    count = cursor.fetchone()[0]
    print(f'✓ Tables in epl_dw database: {count}')
    
    # Check specific tables
    cursor.execute('SHOW TABLES')
    tables = [row[0] for row in cursor.fetchall()]
    
    critical_tables = ['ETL_Events_Manifest', 'ETL_File_Manifest', 'stg_events_raw', 'dim_team', 'fact_match']
    print('\nCritical tables:')
    for table in critical_tables:
        if table in tables:
            print(f'  ✓ {table}')
        else:
            print(f'  ✗ {table} - MISSING!')
    
    print(f'\nAll tables ({count}):\n')
    for table in sorted(tables):
        print(f'  - {table}')
    
    conn.close()
except Error as e:
    print(f'✗ Error: {e}')
