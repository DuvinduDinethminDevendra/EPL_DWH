-- 001_hardening.sql
-- Add recommended production hardening: audit columns, FK behaviors, smaller indexes

-- Audit columns for dims
ALTER TABLE dim_team
  ADD COLUMN IF NOT EXISTS updated_at DATETIME NULL,
  ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100) NULL,
  ADD COLUMN IF NOT EXISTS is_deleted TINYINT(1) NOT NULL DEFAULT 0;

ALTER TABLE dim_player
  ADD COLUMN IF NOT EXISTS updated_at DATETIME NULL,
  ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100) NULL,
  ADD COLUMN IF NOT EXISTS is_deleted TINYINT(1) NOT NULL DEFAULT 0;

ALTER TABLE dim_stadium
  ADD COLUMN IF NOT EXISTS updated_at DATETIME NULL,
  ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100) NULL;

-- FK policies: prefer RESTRICT on dimensions (no accidental cascade)
ALTER TABLE fact_match
  DROP FOREIGN KEY IF EXISTS fact_match_ibfk_3;
ALTER TABLE fact_match
  ADD CONSTRAINT fact_match_ibfk_3 FOREIGN KEY (home_team_id) REFERENCES dim_team(team_id) ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE fact_match
  DROP FOREIGN KEY IF EXISTS fact_match_ibfk_4;
ALTER TABLE fact_match
  ADD CONSTRAINT fact_match_ibfk_4 FOREIGN KEY (away_team_id) REFERENCES dim_team(team_id) ON DELETE RESTRICT ON UPDATE CASCADE;

-- Smaller index for performance: add composite index for typical queries
CREATE INDEX IF NOT EXISTS idx_fact_match_season_date ON fact_match (season_id, date_id);
