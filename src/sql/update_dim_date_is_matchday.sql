-- Update match days from staging table
UPDATE dim_date d
INNER JOIN (
    SELECT DISTINCT DATE(`Date`) as match_date
    FROM stg_e0_match_raw 
    WHERE `Date` IS NOT NULL 
      AND TRIM(`Date`) <> ''
      AND `Date` != '0000-00-00'
) s ON d.cal_date = s.match_date
SET d.is_matchday = 1
WHERE d.is_matchday <> 1;