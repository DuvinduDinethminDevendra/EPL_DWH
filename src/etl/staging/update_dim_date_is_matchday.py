from pathlib import Path
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def update_dim_date_is_matchday(engine):
    """Execute SQL to set dim_date.is_matchday based on stg_e0_match_raw.Date.

    Prefers src/sql/update_dim_date_is_matchday.sql if present, falls back to an
    inline DB-aware SQL statement.
    """
    sql_path = Path(__file__).parent.parent / "sql" / "update_dim_date_is_matchday.sql"

    # If a dedicated SQL file exists use it (assumes it's compatible with your DB)
    if sql_path.exists():
        sql = sql_path.read_text(encoding="utf-8")
    else:
        # Choose SQL per dialect
        dialect = engine.dialect.name.lower()
        if dialect.startswith("postgres"):
            sql = """
            UPDATE dim_date d
            SET is_matchday = TRUE
            FROM (
              SELECT DISTINCT ("Date")::date AS match_date
              FROM stg_e0_match_raw
              WHERE "Date" IS NOT NULL
                AND trim("Date") <> ''
            ) s
            WHERE d.cal_date = s.match_date
              AND coalesce(d.is_matchday::boolean, FALSE) <> TRUE;
            """
        elif dialect.startswith("mysql") or dialect.startswith("mariadb"):
            # Use NULLIF to avoid MySQL strict-mode errors for '0000-00-00'
            sql = """
            UPDATE dim_date d
            INNER JOIN (
              SELECT DISTINCT DATE(NULLIF(`Date`, '0000-00-00')) as match_date
              FROM stg_e0_match_raw
              WHERE `Date` IS NOT NULL
                AND TRIM(`Date`) <> ''
            ) s ON d.cal_date = s.match_date
            SET d.is_matchday = 1
            WHERE d.is_matchday <> 1;
            """
            diagnostic_sql = """
            SELECT 
                COUNT(*) as total_rows,
                COUNT(DISTINCT DATE(NULLIF(`Date`, '0000-00-00'))) as distinct_dates,
                MIN(DATE(NULLIF(`Date`, '0000-00-00'))) as earliest_date,
                MAX(DATE(NULLIF(`Date`, '0000-00-00'))) as latest_date
            FROM stg_e0_match_raw
            WHERE `Date` IS NOT NULL AND TRIM(`Date`) <> ''
            """
        else:
            # Generic fallback: try casting via CAST(... AS DATE), may work on many DBs
            sql = """
            UPDATE dim_date d
            SET is_matchday = 1
            WHERE d.cal_date IN (
              SELECT DISTINCT CAST("Date" AS DATE)
              FROM stg_e0_match_raw
              WHERE "Date" IS NOT NULL AND trim("Date") <> ''
            ) AND d.is_matchday <> 1;
            """

    try:
        with engine.begin() as conn:
            diagnostic_sql = None
            dialect = engine.dialect.name.lower()
            if dialect.startswith("postgres"):
                diagnostic_sql = """
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT ("Date")::date) as distinct_dates,
                    MIN(("Date")::date) as earliest_date,
                    MAX(("Date")::date) as latest_date
                FROM stg_e0_match_raw
                WHERE "Date" IS NOT NULL AND trim("Date") <> ''
                """
            elif dialect.startswith("mysql") or dialect.startswith("mariadb"):
                diagnostic_sql = """
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT DATE(NULLIF(`Date`, '0000-00-00'))) as distinct_dates,
                    MIN(DATE(NULLIF(`Date`, '0000-00-00'))) as earliest_date,
                    MAX(DATE(NULLIF(`Date`, '0000-00-00'))) as latest_date
                FROM stg_e0_match_raw
                WHERE `Date` IS NOT NULL AND TRIM(`Date`) <> ''
                """
            else:
                diagnostic_sql = """
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT CAST("Date" AS DATE)) as distinct_dates,
                    MIN(CAST("Date" AS DATE)) as earliest_date,
                    MAX(CAST("Date" AS DATE)) as latest_date
                FROM stg_e0_match_raw
                WHERE "Date" IS NOT NULL AND trim("Date") <> ''
                """

            diag_result = conn.execute(text(diagnostic_sql)).fetchone()
            # Row can be a RowMapping or tuple; handle both
            try:
                mapping = diag_result._mapping
                total_rows = mapping.get("total_rows")
                distinct_dates = mapping.get("distinct_dates")
                earliest = mapping.get("earliest_date")
                latest = mapping.get("latest_date")
            except Exception:
                total_rows, distinct_dates, earliest, latest = diag_result

            logger.info(f"Date stats - Total rows: {total_rows}, Distinct dates: {distinct_dates}, Range: {earliest} to {latest}")

            # Execute update
            result = conn.execute(text(sql))
            # rowcount may be -1 for some drivers; log whatever is returned
            logger.info(f"Update executed, rowcount reported = {getattr(result, 'rowcount', None)}")

            # Also return or log how many dim_date rows now have is_matchday = true
            post_check = conn.execute(text("SELECT COUNT(*) FROM dim_date WHERE is_matchday IN (1, TRUE)")).fetchone()
            try:
                post_count = post_check._mapping.get("count") if hasattr(post_check, "_mapping") else post_check[0]
            except Exception:
                post_count = post_check[0]
            logger.info(f"Total dim_date rows with is_matchday=1 after update: {post_count}")

            return True

    except Exception as e:
        logger.warning(f"Warning updating dim_date.is_matchday: {e}")
        return False