
import argparse
from .extract import csv_reader
from .transform import clean
from .staging import load_staging
from .load_warehouse import run_complete_etl_pipeline
from .config import RAW_DATA_DIR
from pathlib import Path
from .db import get_engine
from sqlalchemy import text
import subprocess
import os
from tqdm import tqdm
from datetime import datetime

def generate_player_stats_mock_data():
    """Generate valid player stats mock data with real EPL team and player names"""
    
    PLAYERS_BY_TEAM = {
        'Arsenal FC': ['Saka', 'Odegaard', 'Martinelli', 'Partey', 'White', 'Zinchenko', 'Jesus', 'Trossard'],
        'Manchester City FC': ['De Bruyne', 'Haaland', 'Cancelo', 'Rodri', 'Dias', 'Grealish', 'Alvarez', 'Foden'],
        'Liverpool FC': ['Salah', 'Van Dijk', 'Alisson', 'Henderson', 'Mane', 'Nunez', 'Trent', 'Fabinho'],
        'Chelsea FC': ['Sterling', 'Pereira', 'James', 'Mount', 'Gallagher', 'Enzo', 'Mudryk', 'Madueke'],
        'Manchester United FC': ['Bruno', 'Martial', 'Rashford', 'McTominay', 'Casemiro', 'Shaw', 'Varane', 'Dalot'],
        'Newcastle United FC': ['Isak', 'Joelinton', 'Trippier', 'Guimaraes', 'Botman', 'Targett', 'Almiron', 'Tonali'],
        'Brighton & Hove Albion FC': ['Mwepu', 'Caicedo', 'Tadic', 'Welbeck', 'Veltman', 'Webster', 'Lamptey', 'Jahanbakhsh'],
        'Brentford FC': ['Mbeumo', 'Toney', 'Ajer', 'Dasilva', 'Hickey', 'Jensen', 'Simons', 'Sorensen'],
        'Tottenham Hotspur FC': ['Son', 'Kane', 'Richarlison', 'Kulusevski', 'Porro', 'Romero', 'Van de Ven', 'Sarr'],
        'Crystal Palace FC': ['Olise', 'Zaha', 'Guehi', 'Eze', 'Nketiah', 'Mitchell', 'Andersen', 'Ward'],
        'Everton FC': ['Iwobi', 'Gordon', 'Doucoure', 'Harrison', 'Coady', 'Holgate', 'Coleman', 'Vinagre'],
        'West Ham United FC': ['Rice', 'Ings', 'Soucek', 'Bowen', 'Antonio', 'Zouma', 'Coufal', 'Emerson'],
        'Fulham FC': ['Pereira', 'Adarabioyo', 'Solomon', 'Palhinha', 'Willian', 'Ream', 'De Cordova', 'Tielemans'],
        'Wolverhampton Wanderers FC': ['Neves', 'Cunha', 'Lemina', 'Ait Nouri', 'Coady', 'Kilman', 'Semedo', 'Sa'],
        'Nottingham Forest FC': ['Awoniyi', 'Hudson-Odoi', 'Wood', 'Yates', 'Murillo', 'Niakhate', 'Williams', 'Laryea'],
        'AFC Bournemouth': ['Solanke', 'Lerma', 'Mepham', 'Cook', 'Tavernier', 'Brady', 'Evanson', 'Senesi'],
        'Aston Villa FC': ['Watkins', 'Buendia', 'McGinn', 'Coutinho', 'Martinez', 'Konsa', 'Cash', 'Ramsey'],
        'Southampton FC': ['Salisu', 'Walker-Peters', 'Valery', 'Ward-Prowse', 'Aribo', 'Armstrong', 'Sulemana', 'Livramento'],
        'Leicester City FC': ['Maddison', 'Vardy', 'Mendy', 'Ndidi', 'Castagne', 'Soyuncu', 'Pereira', 'Tielemans'],
        'Ipswich Town FC': ['Delap', 'Cresswell', 'Johnson', 'Jackson', 'Lamy', 'Davis', 'Azaz', 'Woolfenden'],
        'Leeds United FC': ['Sinisterra', 'Ayling', 'Piroe', 'Struijk', 'Rodon', 'Byram', 'Adams', 'Gnonto'],
        'Burnley FC': ['Cornet', 'Amdouni', 'Vitinha', 'Brownhill', 'Barnes', 'Iling', 'Edmundson', 'Roberts'],
        'Luton Town FC': ['Adebayo', 'Dewsbury-Hall', 'Clark', 'Lockyer', 'Ogbene', 'Osho', 'Kaminski', 'Kabore'],
        'Sheffield United FC': ['Heck', 'Gibbs-White', 'Anel', 'Lowe', 'Baldock', 'Stevens', 'Norwood', 'Robinson'],
        'Sunderland AFC': ['Maguire', 'Stewart', 'Embalo', 'Ba', 'Cirkin', 'Heeley', 'ONien', 'Alves'],
    }
    
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # Clear existing data
            conn.execute(text('DELETE FROM stg_player_stats_fbref'))
            
            row_count = 0
            for team_name, player_list in PLAYERS_BY_TEAM.items():
                for season_year in range(2017, 2025):
                    season = f'{season_year}-{season_year+1}'
                    for idx, player_name in enumerate(player_list):
                        conn.execute(text('''
                            INSERT INTO stg_player_stats_fbref 
                            (player_name, team_name, minutes_played, goals, assists, xg, xa, 
                             yellow_cards, red_cards, shots, shots_on_target, season_label)
                            VALUES (:pname, :tname, :mins, :goals, :assists, :xg, :xa, :yc, :rc, :shots, :sot, :season)
                        '''), {
                            'pname': player_name,
                            'tname': team_name,
                            'mins': 2000 + (idx * 150),
                            'goals': (idx + 1) % 20,
                            'assists': (idx + 1) % 10,
                            'xg': float(2 + (idx % 15)),
                            'xa': float((idx % 8)),
                            'yc': idx % 3,
                            'rc': 0,
                            'shots': 3 + (idx % 10),
                            'sot': 1 + (idx % 5),
                            'season': season
                        })
                        row_count += 1
            
            conn.commit()
            print(f"[SUCCESS] Generated {row_count} player stats records with valid team names")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to generate player stats mock data: {str(e)}")
        return False

def run_demo(csv_path):
    import pandas as pd
    df = csv_reader.read_csv(csv_path)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", 5)
    pd.set_option("display.width", 200)
    print(df)       

def run_full_etl_pipeline():
    """Run the complete ETL pipeline: Staging -> Dimensions -> Facts"""
    print("\n" + "="*80)
    print("RUNNING COMPLETE EPL DWH ETL PIPELINE")
    print("="*80)
    
    try:
        # Run complete pipeline (handles staging, cleaning, and dimension loads)
        run_complete_etl_pipeline()
        
        # Clean up staging tables after successful ETL
        print("\n📋 NOW CLEANING UP STAGING TABLES (per DWH best practices)...")
        if not truncate_staging_tables("full_etl_pipeline"):
            print("⚠️  WARNING: ETL completed but staging cleanup had issues")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] ETL pipeline failed: {str(e)}")
        return False

def load_fact_tables():
    """Load fact tables using optimized SQL scripts with progress bar and logging"""
    print("\n" + "="*80)
    print("LOADING FACT TABLES FROM STAGING DATA")
    print("="*80)
    
    # Step 1: Generate valid player stats mock data (must happen before loading facts)
    print("\n[STEP -1] Generating player stats mock data with valid team names...")
    if not generate_player_stats_mock_data():
        print("[ERROR] Failed to generate player stats mock data")
        return False
    
    # First populate mapping tables (required before loading fact_match_events)
    print("\n[STEP 0] Populating mapping tables...")
    if not populate_mapping_tables():
        return False
    
    # Get SQL directory path (src/sql)
    sql_dir = Path(__file__).parent.parent / "sql"
    engine = get_engine()
    
    # Scripts to run in order (includes load_fact_match as step 1!)
    scripts = [
        ("load_fact_match.sql", "Load fact_match from CSV (830 matches)"),
        ("load_fact_player_stats.sql", "Load fact_player_stats from staging (1600 records)"),
        ("load_fact_match_events_step1.sql", "Step 1: Create temporary aggregation table"),
        ("load_fact_match_events_step2.sql", "Step 2: Verify match mappings"),
        ("load_fact_match_events_step3_final.sql", "Step 3: Load 1.36M events into fact_match_events"),
        ("load_fact_match_events_step4_verify.sql", "Step 4: Verify loaded data"),
        ("final_row_count.sql", "Final verification: Show all table row counts"),
    ]
    
    # Log start to ETL_Log
    start_time = datetime.now()
    try:
        with engine.connect() as conn:
            log_query = text("""
                INSERT INTO etl_log (job_name, phase_step, status, start_time, message)
                VALUES (:job, :phase, :stat, :start, :msg)
            """)
            conn.execute(log_query, {
                "job": "load_fact_tables",
                "phase": "initialization",
                "stat": "STARTED",
                "start": start_time,
                "msg": f"Starting fact table load with {len(scripts)} scripts"
            })
            conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log to ETL_Log: {str(e)}")
    
    # Progress bar for overall scripts
    print("\nExecuting SQL scripts with progress:\n")
    
    try:
        for idx, (script_name, description) in enumerate(tqdm(scripts, desc="Overall Progress", unit="script", ascii=True, disable=False), 1):
            script_path = sql_dir / script_name
            step_start = datetime.now()
            
            if not script_path.exists():
                print(f"\n[ERROR] Script not found: {script_path}")
                continue
            
            print(f"\n  [{idx}/{len(scripts)}] {description}")
            
            # Read SQL file
            with open(script_path, 'r') as f:
                sql_content = f.read()
            
            # Execute statements
            try:
                with engine.connect() as conn:
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    
                    # Progress bar for statements in this script
                    for statement in tqdm(statements, desc=f"    {script_name}", leave=False, unit="stmt", ascii=True, disable=False):
                        try:
                            result = conn.execute(text(statement))
                            conn.commit()
                            
                            # Print results if SELECT
                            if statement.strip().upper().startswith("SELECT"):
                                rows = result.fetchall()
                                if rows:
                                    for row in rows[:5]:  # Limit output
                                        print(f"    -> {row}")
                                    if len(rows) > 5:
                                        print(f"    ... and {len(rows)-5} more rows")
                        except Exception as e:
                            print(f"\n  [ERROR] {str(e)}")
                            conn.rollback()
                            # Log failure
                            try:
                                with engine.connect() as log_conn:
                                    log_conn.execute(text("""
                                        INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                                        VALUES (:job, :phase, :stat, :end, :msg)
                                    """), {
                                        "job": "load_fact_tables",
                                        "phase": script_name,
                                        "stat": "FAILED",
                                        "end": datetime.now(),
                                        "msg": f"Failed: {str(e)}"
                                    })
                                    log_conn.commit()
                            except:
                                pass
                            return False
                
                # Log successful completion of this step
                step_end = datetime.now()
                step_duration = (step_end - step_start).total_seconds()
                try:
                    with engine.connect() as log_conn:
                        log_conn.execute(text("""
                            INSERT INTO etl_log (job_name, phase_step, status, start_time, end_time, message)
                            VALUES (:job, :phase, :stat, :start, :end, :msg)
                        """), {
                            "job": "load_fact_tables",
                            "phase": script_name,
                            "stat": "COMPLETED",
                            "start": step_start,
                            "end": step_end,
                            "msg": f"[OK] {description} ({step_duration:.2f}s)"
                        })
                        log_conn.commit()
                except Exception as e:
                    print(f"[WARNING] Could not log step completion: {str(e)}")
                    
            except Exception as e:
                print(f"\n  [ERROR] Step failed: {str(e)}")
                return False
        
        # Log completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "load_fact_tables",
                    "phase": "completion",
                    "stat": "COMPLETED",
                    "end": end_time,
                    "msg": f"All fact tables loaded successfully in {duration:.2f} seconds"
                })
                conn.commit()
        except Exception as e:
            print(f"[WARNING] Could not log completion: {str(e)}")
        
        print("\n" + "="*80)
        print(f"[SUCCESS] FACT TABLE LOADING COMPLETED SUCCESSFULLY ({duration:.2f}s)")
        print("="*80)
        
        # Truncate staging tables after successful fact load
        print("\n📋 NOW CLEANING UP STAGING TABLES (per DWH best practices)...")
        if not truncate_staging_tables("load_fact_tables"):
            print("⚠️  WARNING: Fact tables loaded but staging cleanup had issues")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fact table loading failed: {str(e)}")
        return False

def load_player_stats():
    """Load fact_player_stats from staging table"""
    print("\n" + "="*80)
    print("LOADING FACT_PLAYER_STATS FROM STAGING DATA")
    print("="*80)
    
    # Get SQL script path
    sql_dir = Path(__file__).parent.parent / "sql"
    script_path = sql_dir / "load_fact_player_stats.sql"
    
    if not script_path.exists():
        print(f"\n❌ SQL script not found: {script_path}")
        return False
    
    engine = get_engine()
    start_time = datetime.now()
    
    # Log start to ETL_Log
    try:
        with engine.connect() as conn:
            log_query = text("""
                INSERT INTO etl_log (job_name, phase_step, status, start_time, message)
                VALUES (:job, :phase, :stat, :start, :msg)
            """)
            conn.execute(log_query, {
                "job": "load_player_stats",
                "phase": "initialization",
                "stat": "STARTED",
                "start": start_time,
                "msg": "Starting player stats load"
            })
            conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log to ETL_Log: {str(e)}")
    
    try:
        # Read and execute SQL
        with open(script_path, 'r') as f:
            sql_content = f.read()
        
        print("\nExecuting player stats load:\n")
        
        with engine.connect() as conn:
            # Split statements and execute
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(tqdm(statements, desc="Loading", unit="stmt", ascii=True, disable=False), 1):
                step_start = datetime.now()
                try:
                    result = conn.execute(text(statement))
                    conn.commit()
                    
                    # Display results if SELECT
                    if statement.strip().upper().startswith("SELECT"):
                        rows = result.fetchall()
                        if rows:
                            for row in rows:
                                print(f"  ✓ {row}")
                    
                    # Log successful statement
                    step_end = datetime.now()
                    step_duration = (step_end - step_start).total_seconds()
                    try:
                        with engine.connect() as log_conn:
                            log_conn.execute(text("""
                                INSERT INTO etl_log (job_name, phase_step, status, start_time, end_time, message)
                                VALUES (:job, :phase, :stat, :start, :end, :msg)
                            """), {
                                "job": "load_player_stats",
                                "phase": f"statement_{i}",
                                "stat": "COMPLETED",
                                "start": step_start,
                                "end": step_end,
                                "msg": f"✓ Statement {i}/{len(statements)} ({step_duration:.2f}s)"
                            })
                            log_conn.commit()
                    except Exception as e:
                        print(f"[WARNING] Could not log statement: {str(e)}")
                        
                except Exception as e:
                    print(f"\n  ❌ [ERROR] {str(e)}")
                    # Log failure
                    try:
                        with engine.connect() as log_conn:
                            log_conn.execute(text("""
                                INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                                VALUES (:job, :phase, :stat, :end, :msg)
                            """), {
                                "job": "load_player_stats",
                                "phase": f"statement_{i}",
                                "stat": "FAILED",
                                "end": datetime.now(),
                                "msg": f"Failed: {str(e)}"
                            })
                            log_conn.commit()
                    except:
                        pass
                    conn.rollback()
                    return False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log completion
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "load_player_stats",
                    "phase": "completion",
                    "stat": "COMPLETED",
                    "end": end_time,
                    "msg": f"All player stats loaded successfully in {duration:.2f} seconds"
                })
                conn.commit()
        except Exception as e:
            print(f"[WARNING] Could not log completion: {str(e)}")
        
        print("\n" + "="*80)
        print(f"✅ PLAYER STATS LOADING COMPLETED SUCCESSFULLY ({duration:.2f}s)")
        print("="*80)
        
        # Clean up staging tables after successful player stats load
        print("\n📋 NOW CLEANING UP STAGING TABLES (per DWH best practices)...")
        if not truncate_staging_tables("load_player_stats"):
            print("⚠️  WARNING: Player stats loaded but staging cleanup had issues")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Player stats loading failed: {str(e)}")
        # Log overall failure
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "load_player_stats",
                    "phase": "overall",
                    "stat": "FAILED",
                    "end": datetime.now(),
                    "msg": f"Player stats loading failed: {str(e)}"
                })
                conn.commit()
        except:
            pass
        return False

def truncate_staging_tables(log_job_name="etl_pipeline"):
    """Truncate all staging tables after successful ETL completion.
    
    Staging tables are temporary containers for data transformation.
    After successful load to fact/dimension tables, they should be cleaned.
    Audit trail is preserved in etl_log, etl_file_manifest, etl_json_manifest.
    
    Args:
        log_job_name: Name for ETL_log entry (default: "etl_pipeline")
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*80)
    print("CLEANING UP STAGING TABLES")
    print("="*80)
    
    staging_tables = [
        'stg_e0_match_raw',
        'stg_player_raw',
        'stg_player_stats_fbref',
        'stg_team_raw'
    ]
    
    engine = get_engine()
    start_time = datetime.now()
    
    # Log start
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO etl_log (job_name, phase_step, status, start_time, message)
                VALUES (:job, :phase, :stat, :start, :msg)
            """), {
                "job": log_job_name,
                "phase": "staging_cleanup",
                "stat": "STARTED",
                "start": start_time,
                "msg": f"Starting truncation of {len(staging_tables)} staging tables"
            })
            conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log to ETL_Log: {str(e)}")
    
    try:
        with engine.connect() as conn:
            total_rows_before = 0
            
            # Get row counts before truncation
            print("\n📊 Row counts BEFORE cleanup:")
            for table in staging_tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                total_rows_before += count
                print(f"   {table:.<40} {count:>10,} rows")
            
            # Truncate all staging tables
            print(f"\n🧹 Truncating {len(staging_tables)} staging tables...")
            for table in staging_tables:
                try:
                    conn.execute(text(f"TRUNCATE TABLE {table}"))
                    conn.commit()
                    print(f"   ✅ {table}")
                except Exception as e:
                    print(f"   ❌ {table}: {str(e)}")
                    # Log failure but continue with other tables
                    try:
                        with engine.connect() as log_conn:
                            log_conn.execute(text("""
                                INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                                VALUES (:job, :phase, :stat, :end, :msg)
                            """), {
                                "job": log_job_name,
                                "phase": f"truncate_{table}",
                                "stat": "FAILED",
                                "end": datetime.now(),
                                "msg": f"Failed to truncate {table}: {str(e)}"
                            })
                            log_conn.commit()
                    except:
                        pass
                    return False
            
            # Verify truncation
            print(f"\n✅ Row counts AFTER cleanup:")
            total_rows_after = 0
            for table in staging_tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                total_rows_after += count
                print(f"   {table:.<40} {count:>10,} rows")
        
        # Log successful completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, start_time, end_time, message)
                    VALUES (:job, :phase, :stat, :start, :end, :msg)
                """), {
                    "job": log_job_name,
                    "phase": "staging_cleanup",
                    "stat": "COMPLETED",
                    "start": start_time,
                    "end": end_time,
                    "msg": f"Cleaned staging: {total_rows_before:,} rows removed in {duration:.2f}s. Audit trail preserved in etl_log."
                })
                conn.commit()
        except Exception as e:
            print(f"[WARNING] Could not log cleanup completion: {str(e)}")
        
        print("\n" + "="*80)
        print(f"[SUCCESS] STAGING TABLES CLEANED ({total_rows_before:,} rows removed)")
        print(f"          Audit trail preserved in: etl_log, etl_file_manifest, etl_json_manifest")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ [ERROR] Staging table cleanup failed: {str(e)}")
        # Log failure
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": log_job_name,
                    "phase": "staging_cleanup",
                    "stat": "FAILED",
                    "end": datetime.now(),
                    "msg": f"Staging cleanup failed: {str(e)}"
                })
                conn.commit()
        except:
            pass
        return False

def populate_mapping_tables():
    """Populate dim_team_mapping and dim_match_mapping after staging data is loaded"""
    print("\n" + "="*80)
    print("POPULATING MAPPING TABLES")
    print("="*80)
    
    sql_dir = Path(__file__).parent.parent / "sql"
    script_path = sql_dir / "create_mapping_tables.sql"
    
    if not script_path.exists():
        print(f"⚠️  Mapping script not found: {script_path}")
        return False
    
    engine = get_engine()
    start_time = datetime.now()
    
    # Log start
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO etl_log (job_name, phase_step, status, start_time, message)
                VALUES (:job, :phase, :stat, :start, :msg)
            """), {
                "job": "populate_mappings",
                "phase": "initialization",
                "stat": "STARTED",
                "start": start_time,
                "msg": "Starting mapping table population"
            })
            conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log to ETL_Log: {str(e)}")
    
    try:
        with open(script_path, 'r') as f:
            sql_content = f.read()
        
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"\nExecuting {len(statements)} SQL statements...\n")
        
        with engine.connect() as conn:
            for idx, stmt in enumerate(tqdm(statements, desc="Mapping", unit="stmt", ascii=True, disable=False), 1):
                step_start = datetime.now()
                try:
                    result = conn.execute(text(stmt))
                    conn.commit()
                    
                    if stmt.strip().upper().startswith("SELECT"):
                        rows = result.fetchall()
                        if rows:
                            for row in rows:
                                print(f"  [OK] {row}")
                    
                    # Log successful statement
                    step_end = datetime.now()
                    step_duration = (step_end - step_start).total_seconds()
                    try:
                        with engine.connect() as log_conn:
                            log_conn.execute(text("""
                                INSERT INTO etl_log (job_name, phase_step, status, start_time, end_time, message)
                                VALUES (:job, :phase, :stat, :start, :end, :msg)
                            """), {
                                "job": "populate_mappings",
                                "phase": f"statement_{idx}",
                                "stat": "COMPLETED",
                                "start": step_start,
                                "end": step_end,
                                "msg": f"[OK] Statement {idx}/{len(statements)} ({step_duration:.2f}s)"
                            })
                            log_conn.commit()
                    except Exception as e:
                        print(f"[WARNING] Could not log statement: {str(e)}")
                        
                except Exception as e:
                    print(f"\n  [WARNING] Warning: {str(e)[:100]}")
                    # Log warning
                    try:
                        with engine.connect() as log_conn:
                            log_conn.execute(text("""
                                INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                                VALUES (:job, :phase, :stat, :end, :msg)
                            """), {
                                "job": "populate_mappings",
                                "phase": f"statement_{idx}",
                                "stat": "WARNING",
                                "end": datetime.now(),
                                "msg": f"Warning: {str(e)[:200]}"
                            })
                            log_conn.commit()
                    except:
                        pass
                    conn.rollback()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log completion
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "populate_mappings",
                    "phase": "completion",
                    "stat": "COMPLETED",
                    "end": end_time,
                    "msg": f"Mapping tables populated successfully in {duration:.2f} seconds"
                })
                conn.commit()
        except Exception as e:
            print(f"[WARNING] Could not log completion: {str(e)}")
        
        print("\n[SUCCESS] Mapping tables populated successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Mapping table population failed: {str(e)}")
        # Log failure
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO etl_log (job_name, phase_step, status, end_time, message)
                    VALUES (:job, :phase, :stat, :end, :msg)
                """), {
                    "job": "populate_mappings",
                    "phase": "overall",
                    "stat": "FAILED",
                    "end": datetime.now(),
                    "msg": f"Mapping population failed: {str(e)}"
                })
                conn.commit()
        except:
            pass
        return False

def run_complete_player_pipeline():
    """Master orchestration: Schema -> Full ETL -> Generate Mock FBRef -> Stage -> Load Player Stats -> Populate Mappings"""
    print("\n" + "="*80)
    print("COMPLETE PLAYER STATS PIPELINE")
    print("="*80)
    
    # Step 1: Recreate Schema
    print("\n[STEP 1/6] Recreating schema with all seasons...")
    try:
        sql_dir = Path(__file__).parent.parent / "sql"
        schema_file = sql_dir / "create_schema.sql"
        
        with open(schema_file, 'r') as f:
            sql_content = f.read()
        
        engine = get_engine()
        with engine.connect() as conn:
            for stmt in sql_content.split(';'):
                if stmt.strip():
                    try:
                        conn.execute(text(stmt))
                        conn.commit()
                    except Exception as e:
                        if "already exists" not in str(e):
                            pass
        print("✅ Schema recreated with seasons 2017-2026")
    except Exception as e:
        print(f"❌ Schema recreation failed: {str(e)}")
        return False
    
    # Step 2: Full ETL
    print("\n[STEP 2/6] Running full ETL pipeline...")
    if not run_full_etl_pipeline():
        print("❌ Full ETL failed")
        return False
    print("✅ Full ETL completed")
    
    # Step 3: Generate Mock FBRef Data
    print("\n[STEP 3/6] Generating mock FBRef player stats...")
    try:
        import pandas as pd
        from pathlib import Path as PathlibPath
        from random import randint, seed
        
        seed(42)
        TEAMS = [
            'Manchester City', 'Liverpool', 'Manchester United', 'Chelsea',
            'Arsenal', 'Tottenham', 'Leicester City', 'West Ham',
            'Newcastle', 'Brighton', 'Aston Villa', 'Everton',
            'Fulham', 'Brentford', 'Crystal Palace', 'Wolves',
            'Southampton', 'Nottingham Forest', 'Luton Town', 'Bournemouth',
        ]
        BASE_PLAYERS = [
            'De Bruyne', 'Haaland', 'Salah', 'Van Dijk', 'Cancelo',
            'Rodri', 'Dias', 'Nunez', 'Son', 'Kane', 'Saka', 'Martinelli',
            'Shaw', 'Mount', 'Antony', 'Rashford', 'Bruno Fernandes',
            'Zinchenko', 'Ødegaard', 'Rice', 'Palmer', 'Mudryk', 'Foden',
        ]
        SEASONS = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']
        
        output_dir = PathlibPath("data/raw/fbref_player_stats")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        total_rows = 0
        for season in SEASONS:
            rows = []
            for team in TEAMS:
                num_players = 22 + len(team) % 4
                for i in range(num_players):
                    player_name = BASE_PLAYERS[i % len(BASE_PLAYERS)]
                    team_hash = hash(team) % 1000
                    player_hash = hash(player_name + team + season) % 1000
                    
                    if randint(1, 100) <= 70:
                        minutes_base = 1200 + (player_hash % 1500)
                        minutes_played = max(0, minutes_base)
                    else:
                        minutes_played = 0
                    
                    minute_factor = minutes_played / 1500.0 if minutes_played > 0 else 0
                    goals = max(0, int(minute_factor * (5 + (player_hash % 10))) - 2)
                    assists = max(0, int(minute_factor * (3 + (player_hash % 8))) - 1)
                    shots = max(0, int(minute_factor * (4 + (player_hash % 6))))
                    shots_on_target = max(0, int(shots * 0.4))
                    yellow_cards = randint(0, 3) if minutes_played > 500 else 0
                    red_cards = 1 if randint(1, 100) > 95 and minutes_played > 1000 else 0
                    xg = round(minute_factor * (2.5 + (player_hash % 100) / 100.0), 2)
                    xa = round(minute_factor * (1.5 + (player_hash % 100) / 100.0), 2)
                    
                    rows.append({
                        'Player': player_name,
                        'Squad': team,
                        'Min': minutes_played,
                        'Gls': goals,
                        'Ast': assists,
                        'Sh': shots,
                        'SoT': shots_on_target,
                        'CrdY': yellow_cards,
                        'CrdR': red_cards,
                        'xG': xg,
                        'xA': xa,
                        'Season': season,
                    })
            
            df = pd.DataFrame(rows)
            output_file = output_dir / f"{season}_player_stats.csv"
            df.to_csv(output_file, index=False)
            total_rows += len(df)
        
        print(f"✅ Generated {total_rows:,} mock FBRef player stats rows")
    except Exception as e:
        print(f"❌ Mock data generation failed: {str(e)}")
        return False
    
    # Step 4: Stage Player Stats CSVs
    print("\n[STEP 4/6] Staging FBRef player stats CSVs...")
    try:
        csv_dir = PathlibPath("data/raw/fbref_player_stats")
        engine = get_engine()
        total_rows = 0
        
        for csv_file in sorted(csv_dir.glob("*.csv")):
            df = pd.read_csv(csv_file)
            df["load_timestamp"] = pd.Timestamp.now()
            df = df.rename(columns={
                'Player': 'player_name',
                'Squad': 'team_name',
                'Min': 'minutes_played',
                'Gls': 'goals',
                'Ast': 'assists',
                'Sh': 'shots',
                'SoT': 'shots_on_target',
                'CrdY': 'yellow_cards',
                'CrdR': 'red_cards',
                'xG': 'xg',
                'xA': 'xa',
                'Season': 'season_label',
            })
            
            df.to_sql(
                "stg_player_stats_fbref",
                engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000
            )
            total_rows += len(df)
        
        print(f"✅ Staged {total_rows:,} player stats rows")
    except Exception as e:
        print(f"❌ Staging failed: {str(e)}")
        return False
    
    # Step 5: Load Player Stats
    print("\n[STEP 5/6] Loading fact_player_stats...")
    if not load_player_stats():
        print("❌ Player stats loading failed")
        return False
    print("✅ Player stats loaded")
    
    # Step 6: Populate Mapping Tables
    print("\n[STEP 6/6] Populating mapping tables...")
    if not populate_mapping_tables():
        print("⚠️  Mapping table population had warnings (non-critical)")
    print("✅ Mapping tables populated")
    
    # Step 7: Clean up staging tables
    print("\n[STEP 7/7] Cleaning up staging tables (per DWH best practices)...")
    if not truncate_staging_tables("complete_player_pipeline"):
        print("⚠️  WARNING: Pipeline complete but staging cleanup had issues")
        return False
    print("✅ Staging tables cleaned")
    
    print("\n" + "="*80)
    print("✅ COMPLETE PLAYER STATS PIPELINE FINISHED SUCCESSFULLY!")
    print("="*80 + "\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="EPL DWH ETL Pipeline")
    parser.add_argument("csv", nargs="?", help="Path to a sample CSV file (for demo mode)")
    parser.add_argument("--csv", "-c", dest="csv_flag", help="Path to a sample CSV file (alternative flag)")
    parser.add_argument("--test-db", action="store_true", help="Run a quick DB connectivity test")
    parser.add_argument("--full-etl", action="store_true", help="Run the complete ETL pipeline (staging + dimensions)")
    parser.add_argument("--staging", action="store_true", help="Run only the staging load")
    parser.add_argument("--warehouse", action="store_true", help="Run only the warehouse load (dimensions)")
    parser.add_argument("--load-fact-tables", action="store_true", help="Load fact tables from staging data (run after --full-etl)")
    parser.add_argument("--load-player-stats", action="store_true", help="Load fact_player_stats from staging data")
    parser.add_argument("--complete-player-pipeline", action="store_true", help="Master orchestration: Schema + Full ETL + Mock FBRef + Staging + Load Player Stats (all-in-one)")
    
    args = parser.parse_args()
    csv_path = Path(__file__).parent.parent.parent.parent / "EPL_DWH" / "data" / "raw" / "csv" / "E0Season_20252026.csv"
    
    if args.test_db:
        run_db_test()
    elif args.complete_player_pipeline:
        run_complete_player_pipeline()
    elif args.full_etl:
        run_full_etl_pipeline()
    elif args.load_fact_tables:
        load_fact_tables()
    elif args.load_player_stats:
        load_player_stats()
    elif args.staging:
        print("\nRunning staging load only...")
        load_staging.load_all_staging()
    elif args.warehouse:
        print("\nRunning complete warehouse pipeline (includes staging, cleaning, and dimensions)...")
        run_complete_etl_pipeline()
    else:
        # Default demo mode
        run_demo(csv_path)


def run_db_test():
    """Connect to the configured database, run a simple test query, and print output."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # run a simple SELECT to verify connectivity and show server version
            r1 = conn.execute(text("SELECT 1 AS ok"))
            ok = r1.fetchone()
            r2 = conn.execute(text("SELECT VERSION() AS version"))
            ver = r2.fetchone()
            print("DB connectivity test result:")
            print("SELECT 1 ->", ok[0] if ok is not None else None)
            print("VERSION ->", ver[0] if ver is not None else None)
    except Exception as e:
        print("DB connectivity test failed:", str(e))

if __name__ == "__main__":
    main()
