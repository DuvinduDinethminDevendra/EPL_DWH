"""Clean and upsert dimension tables from staging tables.

This module provides idempotent, re-entrant functions to transform and load
dimension tables using INSERT...ON DUPLICATE KEY UPDATE (MySQL dialect).

Each upsert function:
1. Reads distinct records from staging table
2. Cleanses the data
3. Upserts to corresponding dimension table
4. Logs the operation to etl_log table

Exposed functions:
- upsert_dim_player(engine) -> (rows_inserted, rows_updated)
- upsert_dim_team(engine) -> (rows_inserted, rows_updated)
- upsert_dim_stadium(engine) -> (rows_inserted, rows_updated)
- upsert_dim_referee(engine) -> (rows_inserted, rows_updated)

Private helpers:
- _log_run(engine, process, rows, status, msg) -> None
"""

from datetime import datetime
from typing import Tuple
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.exc import SQLAlchemyError


def _log_run(
    engine: Engine,
    process: str,
    rows: int,
    status: str,
    msg: str = ""
) -> None:
    """Log a dimension upsert operation to etl_log table.
    
    Private helper function to centralize logging across all upsert operations.
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
        process: Name of the process (e.g., "upsert_dim_player")
        rows: Number of rows affected (inserted + updated)
        status: Operation status ('SUCCESS', 'FAILED', 'PARTIAL')
        msg: Optional message for additional context
    
    Returns:
        None
    """
    try:
        with engine.connect() as conn:
            insert_log = text("""
                INSERT INTO etl_log 
                (job_name, phase_step, status, start_time, end_time, rows_processed, message)
                VALUES (:job_name, :phase_step, :status, :start_time, :end_time, :rows_processed, :message)
            """)
            
            conn.execute(insert_log, {
                "job_name": process,
                "phase_step": "transform",
                "status": status,
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "rows_processed": rows,
                "message": msg
            })
            conn.commit()
    except SQLAlchemyError as e:
        print(f"[WARNING] Failed to log operation {process}: {e}")


def check_staging_data_quality(engine: Engine) -> dict:
    """Check data quality in staging tables before upsert.
    
    This function inspects the staging tables to identify:
    - NULL values in key columns
    - Empty strings and whitespace
    - Data completeness
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
    
    Returns:
        Dictionary with data quality metrics
    """
    print("\n" + "="*70)
    print("DATA QUALITY CHECK - STAGING TABLES")
    print("="*70)
    
    quality_report = {}
    
    try:
        with engine.connect() as conn:
            # Check referee data
            print("\n[Referee Data Quality]")
            referee_sql = text("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN referee_name IS NULL OR TRIM(referee_name) = '' THEN 1 ELSE 0 END) as missing_name,
                    SUM(CASE WHEN date_of_birth IS NULL THEN 1 ELSE 0 END) as missing_dob,
                    SUM(CASE WHEN nationality IS NULL OR TRIM(nationality) = '' THEN 1 ELSE 0 END) as missing_nationality,
                    SUM(CASE WHEN premier_league_debut IS NULL THEN 1 ELSE 0 END) as missing_debut,
                    SUM(CASE WHEN ref_status IS NULL OR TRIM(ref_status) = '' THEN 1 ELSE 0 END) as missing_status
                FROM stg_referee_raw
                WHERE status = 'LOADED'
            """)
            
            result = conn.execute(referee_sql).fetchone()
            if result:
                total, missing_name, missing_dob, missing_nat, missing_debut, missing_status = result
                quality_report['referee'] = {
                    'total': total or 0,
                    'missing_name': missing_name or 0,
                    'missing_dob': missing_dob or 0,
                    'missing_nationality': missing_nat or 0,
                    'missing_debut': missing_debut or 0,
                    'missing_status': missing_status or 0
                }
                print(f"  Total Records: {total}")
                print(f"  Missing Referee Name: {missing_name}")
                print(f"  Missing Date of Birth: {missing_dob}")
                print(f"  Missing Nationality: {missing_nat}")
                print(f"  Missing PL Debut: {missing_debut}")
                print(f"  Missing Status: {missing_status}")
    
    except SQLAlchemyError as e:
        print(f"[WARNING] Error during quality check: {e}")
    
    print("="*70 + "\n")
    return quality_report


def upsert_dim_player(engine: Engine) -> Tuple[int, int]:
    """Upserts players using a single, robust, idempotent INSERT...ON DUPLICATE KEY UPDATE."""
    process_name = "upsert_dim_player"
    rows_affected = 0
    status = "SUCCESS"
    msg = ""

    # This single query handles insertion of new players and updates of existing ones.
    # It uses a subquery to select distinct players and their most complete JSON data.
    # The ON DUPLICATE KEY UPDATE clause uses COALESCE to avoid overwriting
    # existing data with NULLs if a less complete record is processed.
    sql = text("""
        INSERT INTO dim_player (
            external_id,
            player_name,
            birth_date,
            nationality,
            position,
            player_bk
        )
        SELECT
            s.player_id_str,
            s.player_name,
            s.birth_date,
            s.nationality,
            s.position,
            s.player_id_str
        FROM (
            SELECT DISTINCT
                CAST(player_id AS CHAR) AS player_id_str,
                TRIM(player_name) AS player_name,
                STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(raw_data, '$.dateOfBirth')), '%b %d, %Y') AS birth_date,
                JSON_UNQUOTE(JSON_EXTRACT(raw_data, '$.nationality[0]')) AS nationality,
                JSON_UNQUOTE(JSON_EXTRACT(raw_data, '$.position')) AS position
            FROM stg_player_raw
            WHERE status = 'SUCCESS' AND player_name IS NOT NULL AND TRIM(player_name) <> ''
        ) AS s
        ON DUPLICATE KEY UPDATE
            player_name = VALUES(player_name),
            birth_date = COALESCE(VALUES(birth_date), dim_player.birth_date),
            nationality = COALESCE(VALUES(nationality), dim_player.nationality),
            position = COALESCE(VALUES(position), dim_player.position),
            player_bk = VALUES(player_bk);
    """)

    try:
        with engine.begin() as conn:
            result = conn.execute(sql)
            rows_affected = result.rowcount or 0
            msg = f"Upserted {rows_affected} player records from JSON."
            print(f"[OK] {process_name}: {msg}")
    except SQLAlchemyError as e:
        status, msg = "FAILED", str(e)
        print(f"[ERROR] {process_name}: {msg}")
        raise
    finally:
        _log_run(engine, process_name, rows_affected, status, msg)

    return (rows_affected, 0)


def upsert_dim_team(engine: Engine) -> Tuple[int, int]:
    """Upsert distinct teams from stg_team_raw to dim_team.
    
    Business key: team_name
    Columns populated: team_name, team_code, city
    
    Data flow:
    1. Extract distinct teams from stg_team_raw with team_code and city
    2. team_code: from shortName field
    3. city: extracted from address field (first part before comma)
    4. Clean: strip whitespace, remove NULL values
    5. Upsert to dim_team with ON DUPLICATE KEY UPDATE
    6. Log operation to etl_log
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
    
    Returns:
        Tuple of (rows_inserted, rows_updated)
        Note: MySQL ON DUPLICATE KEY UPDATE does not distinguish between insert/update,
              so we return (total_affected, 0) for compatibility
    
    Raises:
        SQLAlchemyError: if database operation fails
    """
    process_name = "upsert_dim_team"
    rows_affected = 0
    status = "SUCCESS"
    msg = ""
    
    try:
        with engine.begin() as conn:
            # Upsert distinct teams from staging to dimension
            # City extraction: get the word before the last postcode segment
            # UK postcodes are format "XX# #XX" so we extract the word before last 2 words
            upsert_sql = text("""
                INSERT INTO dim_team (team_name, team_code, city)
                SELECT DISTINCT 
                    TRIM(name) AS team_name,
                    COALESCE(TRIM(shortName), TRIM(tla)) AS team_code,
                    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', -3), ' ', 1)) AS city
                FROM stg_team_raw
                WHERE name IS NOT NULL 
                  AND TRIM(name) != ''
                ON DUPLICATE KEY UPDATE
                    team_name = VALUES(team_name),
                    team_code = COALESCE(VALUES(team_code), dim_team.team_code),
                    city = COALESCE(VALUES(city), dim_team.city)
            """)
            
            result = conn.execute(upsert_sql)
            rows_affected = result.rowcount or 0
            msg = f"Upserted {rows_affected} distinct team records"
            
    except SQLAlchemyError as e:
        status = "FAILED"
        msg = f"Error during team upsert: {str(e)}"
        print(f"[ERROR] {process_name}: {msg}")
        raise
    
    finally:
        _log_run(engine, process_name, rows_affected, status, msg)
    
    return (rows_affected, 0)


def upsert_dim_stadium(engine: Engine) -> Tuple[int, int]:
    """Upsert distinct stadiums from stg_e0_match_raw to dim_stadium.
    
    Business key: stadium_name (stadium venue)
    
    Data flow:
    1. Extract distinct venue from stg_e0_match_raw (HomeTeam venue)
    2. Clean: strip whitespace, remove NULL values
    3. Upsert to dim_stadium with ON DUPLICATE KEY UPDATE
    4. Log operation to etl_log
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
    
    Returns:
        Tuple of (rows_inserted, rows_updated)
        Note: MySQL ON DUPLICATE KEY UPDATE does not distinguish between insert/update,
              so we return (total_affected, 0) for compatibility
    
    Raises:
        SQLAlchemyError: if database operation fails
    """
    process_name = "upsert_dim_stadium"
    rows_affected = 0
    status = "SUCCESS"
    msg = ""
    
    try:
        with engine.begin() as conn:
            # Upsert distinct stadiums from stg_e0_match_raw
            upsert_sql = text("""
                INSERT INTO dim_stadium (stadium_name)
                SELECT DISTINCT 
                    TRIM(HomeTeam) AS stadium_name
                FROM stg_e0_match_raw
                WHERE HomeTeam IS NOT NULL
                ON DUPLICATE KEY UPDATE
                    stadium_name = VALUES(stadium_name)
            """)
            
            result = conn.execute(upsert_sql)
            rows_affected = result.rowcount or 0
            msg = f"Upserted {rows_affected} distinct stadium records"
            
    except SQLAlchemyError as e:
        status = "FAILED"
        msg = f"Error during stadium upsert: {str(e)}"
        print(f"[ERROR] {process_name}: {msg}")
        raise
    
    finally:
        _log_run(engine, process_name, rows_affected, status, msg)
    
    return (rows_affected, 0)


def upsert_dim_referee(engine: Engine) -> Tuple[int, int]:
    """Upsert distinct referees from stg_referee_raw to dim_referee.
    
    Business key: referee_name
    
    Data flow:
    1. Extract distinct referees from stg_referee_raw
    2. Clean: strip whitespace, handle NULL values, parse dates
    3. Upsert to dim_referee with ON DUPLICATE KEY UPDATE
    4. Log operation to etl_log
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
    
    Returns:
        Tuple of (rows_inserted, rows_updated)
        Note: MySQL ON DUPLICATE KEY UPDATE does not distinguish between insert/update,
              so we return (total_affected, 0) for compatibility
    
    Raises:
        SQLAlchemyError: if database operation fails
    """
    process_name = "upsert_dim_referee"
    rows_affected = 0
    status = "SUCCESS"
    msg = ""
    
    try:
        with engine.begin() as conn:
            # First, try to upsert from stg_referee_raw (Excel data with full details)
            upsert_sql = text("""
                INSERT INTO dim_referee (
                    referee_name,
                    date_of_birth,
                    nationality,
                    premier_league_debut,
                    status,
                    referee_bk
                )
                SELECT DISTINCT 
                    TRIM(referee_name) AS referee_name,
                    date_of_birth,
                    TRIM(nationality) AS nationality,
                    premier_league_debut,
                    TRIM(ref_status) AS status,
                    TRIM(referee_name) AS referee_bk
                FROM stg_referee_raw
                WHERE referee_name IS NOT NULL
                  AND TRIM(referee_name) != ''
                  AND status = 'LOADED'
                ON DUPLICATE KEY UPDATE
                    referee_name = VALUES(referee_name),
                    date_of_birth = COALESCE(VALUES(date_of_birth), dim_referee.date_of_birth),
                    nationality = COALESCE(VALUES(nationality), dim_referee.nationality),
                    premier_league_debut = COALESCE(VALUES(premier_league_debut), dim_referee.premier_league_debut),
                    status = COALESCE(VALUES(status), dim_referee.status),
                    referee_bk = VALUES(referee_bk)
            """)
            
            result = conn.execute(upsert_sql)
            rows_affected = result.rowcount or 0
            msg = f"Upserted {rows_affected} distinct referee records from Excel"
            
    except SQLAlchemyError as e:
        status = "FAILED"
        msg = f"Error during referee upsert: {str(e)}"
        print(f"[ERROR] {process_name}: {msg}")
        raise
    
    finally:
        _log_run(engine, process_name, rows_affected, status, msg)
    
    return (rows_affected, 0)


def run_all_upserts(engine: Engine) -> dict:
    """Execute all dimension upserts in sequence.
    
    This is the main orchestration function that runs all four upsert operations
    in a defined order: Players → Teams → Stadiums → Referees.
    
    Each upsert is wrapped in error handling to allow subsequent operations
    to continue even if one fails.
    
    Args:
        engine: SQLAlchemy engine connected to the data warehouse
    
    Returns:
        Dictionary with summary of all operations:
        {
            'dim_player': (inserted, updated),
            'dim_team': (inserted, updated),
            'dim_stadium': (inserted, updated),
            'dim_referee': (inserted, updated),
            'total_rows': total number of rows affected,
            'success': boolean indicating all operations succeeded
        }
    """
    results = {
        'dim_player': (0, 0),
        'dim_team': (0, 0),
        'dim_stadium': (0, 0),
        'dim_referee': (0, 0),
        'total_rows': 0,
        'success': True
    }
    
    print("\n" + "="*70)
    print("DIMENSION TABLE UPSERT ORCHESTRATION")
    print("="*70)
    
    # Check data quality before upserting
    quality_report = check_staging_data_quality(engine)
    
    # Upsert Players
    print("\n[1/4] Upserting dim_player...")
    try:
        inserted, updated = upsert_dim_player(engine)
        results['dim_player'] = (inserted, updated)
        print(f"    [OK] dim_player: {inserted} rows affected")
    except Exception as e:
        print(f"    [ERROR] dim_player failed: {e}")
        results['success'] = False
    
    # Upsert Teams
    print("\n[2/4] Upserting dim_team...")
    try:
        inserted, updated = upsert_dim_team(engine)
        results['dim_team'] = (inserted, updated)
        print(f"    [OK] dim_team: {inserted} rows affected")
    except Exception as e:
        print(f"    [ERROR] dim_team failed: {e}")
        results['success'] = False
    
    # Upsert Stadiums
    print("\n[3/4] Upserting dim_stadium...")
    try:
        inserted, updated = upsert_dim_stadium(engine)
        results['dim_stadium'] = (inserted, updated)
        print(f"    [OK] dim_stadium: {inserted} rows affected")
    except Exception as e:
        print(f"    [ERROR] dim_stadium failed: {e}")
        results['success'] = False
    
    # Upsert Referees
    print("\n[4/4] Upserting dim_referee...")
    try:
        inserted, updated = upsert_dim_referee(engine)
        results['dim_referee'] = (inserted, updated)
        print(f"    [OK] dim_referee: {inserted} rows affected")
    except Exception as e:
        print(f"    [ERROR] dim_referee failed: {e}")
        results['success'] = False
    
    # Calculate totals
    total = sum(ins + upd for ins, upd in [
        results['dim_player'],
        results['dim_team'],
        results['dim_stadium'],
        results['dim_referee']
    ])
    results['total_rows'] = total
    
    # Print summary
    print("\n" + "="*70)
    print("UPSERT SUMMARY")
    print("="*70)
    print(f"dim_player:  {results['dim_player'][0]:6d} rows affected")
    print(f"dim_team:    {results['dim_team'][0]:6d} rows affected")
    print(f"dim_stadium: {results['dim_stadium'][0]:6d} rows affected")
    print(f"dim_referee: {results['dim_referee'][0]:6d} rows affected")
    print("-"*70)
    print(f"TOTAL:       {total:6d} rows affected")
    print(f"Status:      {'[OK] SUCCESS' if results['success'] else '[ERROR] FAILED'}")
    print("="*70 + "\n")
    
    return results


if __name__ == "__main__":
    """Main entry point: use project's config to build engine and run all upserts."""
    
    # Import project config
    try:
        from ..db import get_engine
        engine = get_engine()
    except ImportError:
        # Fallback if run directly with relative imports
        print("[ERROR] Cannot import project's database configuration")
        exit(1)
    
    print("\n[INFO] Connecting to database using project configuration")
    
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("[OK] Database connection successful\n")
        
        # Run all upsert operations
        results = run_all_upserts(engine)
        
        # Exit with appropriate code
        exit_code = 0 if results['success'] else 1
        exit(exit_code)
    
    except SQLAlchemyError as e:
        print(f"\n[ERROR] Database error: {e}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        exit(1)
