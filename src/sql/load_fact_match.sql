-- ================================================================================================
--  Load Fact Match Table
-- ================================================================================================
--  Description: This script performs an idempotent load into the `fact_match` table.
--  Source:      `stg_e0_match_raw`
--  Target:      `fact_match`
--  Idempotency: Achieved via `INSERT ... ON DUPLICATE KEY UPDATE`. The `match_source_key`
--               is the unique business key.
--  Sentinel:    Uses -1 for any dimension lookup that fails.
-- ================================================================================================

-- Step 1: Perform the idempotent upsert into the fact table.
-- A Common Table Expression (CTE) is used to first conform the raw team names
-- from staging into the standard names used in the dimension tables.
INSERT INTO fact_match (
    -- Business Key
    match_source_key,

    -- Dimension Foreign Keys
    date_id,
    season_id,
    home_team_id,
    away_team_id,
    referee_id,
    stadium_id,

    -- Core Match Metrics
    home_goals,
    away_goals,
    match_result,
    half_time_home_goals,
    half_time_away_goals,

    -- Detailed Match Stats
    home_shots_total,
    away_shots_total,
    home_shots_on_target,
    away_shots_on_target,
    home_fouls,
    away_fouls,
    home_corners,
    away_corners,
    home_yellow_cards,
    away_yellow_cards,
    home_red_cards,
    away_red_cards,

    -- Other Attributes
    attendance
)
WITH stg_e0_match_raw_conformed AS (
    SELECT
        *,
        CASE TRIM(HomeTeam)
            WHEN 'Man City' THEN 'Manchester City FC'
            WHEN 'Man United' THEN 'Manchester United FC'
            WHEN 'Nott''m Forest' THEN 'Nottingham Forest FC'
            WHEN 'Wolves' THEN 'Wolverhampton Wanderers FC'
            WHEN 'Bournemouth' THEN 'AFC Bournemouth'
            WHEN 'Brighton' THEN 'Brighton & Hove Albion FC'
            WHEN 'Newcastle' THEN 'Newcastle United FC'
            WHEN 'Sheffield United' THEN 'Sheffield United FC'
            WHEN 'West Ham' THEN 'West Ham United FC'
            WHEN 'Tottenham' THEN 'Tottenham Hotspur FC'
            WHEN 'Luton' THEN 'Luton Town FC'
            WHEN 'Ipswich' THEN 'Ipswich Town FC'
            WHEN 'Leicester' THEN 'Leicester City FC'
            WHEN 'Southampton' THEN 'Southampton FC'
            WHEN 'Sunderland' THEN 'Sunderland AFC'
            WHEN 'Leeds' THEN 'Leeds United FC'
            WHEN 'Arsenal' THEN 'Arsenal FC'
            WHEN 'Chelsea' THEN 'Chelsea FC'
            WHEN 'Liverpool' THEN 'Liverpool FC'
            WHEN 'Everton' THEN 'Everton FC'
            WHEN 'Fulham' THEN 'Fulham FC'
            WHEN 'Burnley' THEN 'Burnley FC'
            WHEN 'Crystal Palace' THEN 'Crystal Palace FC'
            WHEN 'Brentford' THEN 'Brentford FC'
            WHEN 'Aston Villa' THEN 'Aston Villa FC'
            ELSE TRIM(HomeTeam)
        END AS HomeTeam_conformed,
        CASE TRIM(AwayTeam)
            WHEN 'Man City' THEN 'Manchester City FC'
            WHEN 'Man United' THEN 'Manchester United FC'
            WHEN 'Nott''m Forest' THEN 'Nottingham Forest FC'
            WHEN 'Wolves' THEN 'Wolverhampton Wanderers FC'
            WHEN 'Bournemouth' THEN 'AFC Bournemouth'
            WHEN 'Brighton' THEN 'Brighton & Hove Albion FC'
            WHEN 'Newcastle' THEN 'Newcastle United FC'
            WHEN 'Sheffield United' THEN 'Sheffield United FC'
            WHEN 'West Ham' THEN 'West Ham United FC'
            WHEN 'Tottenham' THEN 'Tottenham Hotspur FC'
            WHEN 'Luton' THEN 'Luton Town FC'
            WHEN 'Ipswich' THEN 'Ipswich Town FC'
            WHEN 'Leicester' THEN 'Leicester City FC'
            WHEN 'Southampton' THEN 'Southampton FC'
            WHEN 'Sunderland' THEN 'Sunderland AFC'
            WHEN 'Leeds' THEN 'Leeds United FC'
            WHEN 'Arsenal' THEN 'Arsenal FC'
            WHEN 'Chelsea' THEN 'Chelsea FC'
            WHEN 'Liverpool' THEN 'Liverpool FC'
            WHEN 'Everton' THEN 'Everton FC'
            WHEN 'Fulham' THEN 'Fulham FC'
            WHEN 'Burnley' THEN 'Burnley FC'
            WHEN 'Crystal Palace' THEN 'Crystal Palace FC'
            WHEN 'Brentford' THEN 'Brentford FC'
            WHEN 'Aston Villa' THEN 'Aston Villa FC'
            ELSE TRIM(AwayTeam)
        END AS AwayTeam_conformed
    FROM stg_e0_match_raw
)
SELECT
    -- Business Key: Unique identifier for a match from the source file.
    CONCAT(s.Div, s.Date, s.HomeTeam_conformed, s.AwayTeam_conformed) AS match_source_key,

    -- Dimension Lookups (with -1 sentinel for not found)
    COALESCE(dd.date_id, -1) AS date_id,           -- from dim_date
    COALESCE(ds.season_id, -1) AS season_id,         -- from dim_season
    COALESCE(dth.team_id, -1) AS home_team_id,      -- from dim_team (Home)
    COALESCE(dta.team_id, -1) AS away_team_id,      -- from dim_team (Away)
    COALESCE(dr.referee_id, -1) AS referee_id,        -- from dim_referee
    COALESCE(dst.stadium_id, -1) AS stadium_id,        -- from dim_stadium

    -- Core Match Metrics
    s.FTHG AS home_goals,
    s.FTAG AS away_goals,
    s.FTR AS match_result,
    s.HTHG AS half_time_home_goals,
    s.HTAG AS half_time_away_goals,

    -- Detailed Match Stats
    s.HS AS home_shots_total,
    s.AS AS away_shots_total,
    s.HST AS home_shots_on_target,
    s.AST AS away_shots_on_target,
    s.HF AS home_fouls,
    s.AF AS away_fouls,
    s.HC AS home_corners,
    s.AC AS away_corners,
    s.HY AS home_yellow_cards,
    s.AY AS away_yellow_cards,
    s.HR AS home_red_cards,
    s.AR AS away_red_cards,

    -- Other Attributes
    NULL AS attendance -- Per requirement, always NULL for now.

FROM
    stg_e0_match_raw_conformed s
LEFT JOIN dim_date dd ON dd.cal_date = s.Date
LEFT JOIN dim_season ds ON ds.season_name = s.Season
LEFT JOIN dim_team dth ON dth.team_name = s.HomeTeam_conformed
LEFT JOIN dim_team dta ON dta.team_name = s.AwayTeam_conformed
LEFT JOIN dim_referee dr ON dr.referee_name = TRIM(s.Referee)
LEFT JOIN dim_stadium dst ON dst.stadium_name = s.HomeTeam_conformed -- Stadium is mapped by HomeTeam name

ON DUPLICATE KEY UPDATE
    -- If a match already exists, only update the metrics, not the dimension keys.
    home_goals = VALUES(home_goals),
    away_goals = VALUES(away_goals),
    match_result = VALUES(match_result),
    half_time_home_goals = VALUES(half_time_home_goals),
    half_time_away_goals = VALUES(half_time_away_goals),
    home_shots_total = VALUES(home_shots_total),
    away_shots_total = VALUES(away_shots_total),
    home_shots_on_target = VALUES(home_shots_on_target),
    away_shots_on_target = VALUES(away_shots_on_target),
    home_fouls = VALUES(home_fouls),
    away_fouls = VALUES(away_fouls),
    home_corners = VALUES(home_corners),
    away_corners = VALUES(away_corners),
    home_yellow_cards = VALUES(home_yellow_cards),
    away_yellow_cards = VALUES(away_yellow_cards),
    home_red_cards = VALUES(home_red_cards),
    away_red_cards = VALUES(away_red_cards),
    attendance = VALUES(attendance);

-- Step 2: Produce the summary row.
-- ROW_COUNT() returns total rows affected by the last statement.
-- In MySQL, for INSERT...UPDATE, this is:
-- 1 for each new row inserted.
-- 2 for each existing row that was updated.
-- 0 for each existing row that was ignored.
-- We derive inserted vs. updated counts from this total.
SET @total_affected = ROW_COUNT();
SET @rows_updated = (@total_affected - (SELECT COUNT(*) FROM fact_match WHERE created_at > NOW() - INTERVAL 5 SECOND)) / 2;
SET @rows_inserted = @total_affected - (@rows_updated * 2);

SELECT
    @rows_inserted AS rows_inserted,
    @rows_updated AS rows_updated,
    @total_affected AS total_affected;

-- Step 3: Log the operation to the ETL log table.
INSERT INTO etl_log (
    job_name,
    phase_step,
    status,
    start_time,
    end_time,
    rows_processed,
    message
)
VALUES (
    'load_fact_match',
    'load',
    'SUCCESS',
    NOW(),
    NOW(),
    @total_affected,
    CONCAT(
        'Upsert completed. Inserted: ', @rows_inserted,
        ', Updated: ', @rows_updated,
        ', Total Affected: ', @total_affected
    )
);
