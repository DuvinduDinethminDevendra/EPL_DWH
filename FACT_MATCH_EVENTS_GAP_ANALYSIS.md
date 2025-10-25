# Analysis: Missing Data for fact_match_events Population

## Current Status

**Table:** `fact_match_events`
**Current Records:** 0
**Required Records:** Depends on data source availability

### Table Structure
```sql
CREATE TABLE fact_match_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL (FK to fact_match),
    event_type VARCHAR(50),          -- Type of event (Goal, Yellow Card, Red Card, Substitution, etc.)
    player_id INT,                   -- FK to dim_player
    team_id INT,                     -- FK to dim_team
    minute INT,                      -- Time in match when event occurred
    extra_time INT DEFAULT 0,        -- Extra time minutes (0 if not applicable)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

## Data Requirements Analysis

### What We Need:
1. **Match Events Data Source** (CRITICAL - MISSING)
   - Event ID / Unique identifier
   - Match ID (to link to fact_match)
   - Event type (Goal, Yellow Card, Red Card, Substitution, Tackle, Save, etc.)
   - Player ID (who performed the action)
   - Team ID (which team performed the action)
   - Minute (when in the match)
   - Extra time indicator

2. **Data Format Options:**
   - CSV: One row per event
   - JSON: Array of events per match
   - API: Real-time event data from football-data.org or similar
   - SQL Dump: Direct database export

### Current Data Sources Status

| Source | Format | Contains Event Data? | Status |
|--------|--------|----------------------|--------|
| CSV files (`data/raw/csv/*.csv`) | CSV | ❌ NO - Only match summaries (goals, cards counts) | ❌ Missing |
| JSON files (`data/raw/json/`) | JSON | ❓ Unknown - Need to check | ⚠️ Needs investigation |
| Excel files (`data/raw/xlsx/`) | XLSX | ❌ NO - Only referees & stadiums | ❌ Missing |
| football-data.org API | REST API | ✅ YES - Event data available | ⚠️ Not integrated yet |

---

## Detailed Gap Analysis

### 1. CSV Data (Currently Loaded)
**File:** `E0Season_*.csv`
**Columns:** Div, Date, HomeTeam, AwayTeam, FTHG, FTAG, Referee, HS, HST, HY, HR, etc.
**Contains Events?** ❌ **NO**
- Only aggregate match statistics
- e.g., "HY=2" (Home Yellow cards count) not individual events
- Would need to disaggregate to create events

**Action Needed:** Cannot use directly; would require event-level data

### 2. JSON Player Data (Currently Loaded)
**Directory:** `data/raw/json/`
**Content:** Player statistics, positions, attributes
**Contains Match Events?** ❌ **NO**
- Player-level career data
- No match-specific events

**Action Needed:** Cannot use directly

### 3. Excel Data (Currently Loaded)
**Files:** Referees & Stadium data
**Contains Events?** ❌ **NO**
- Administrative data only

**Action Needed:** Cannot use directly

### 4. Football-Data.org API
**Endpoint:** `/competitions/PL/matches/{id}/events` (hypothetical)
**Availability:** ✅ YES (if API plan includes events)
**Status:** Currently integrated for team data only, not events

**Action Needed:** 
- Check API subscription plan
- Implement event endpoint integration
- Add to `src/etl/extract/api_client.py`

---

## Solutions to Populate fact_match_events

### Option 1: Synthetic Event Generation (Quick Start - Recommended)
Generate plausible events from existing match aggregates in `stg_e0_match_raw`

**Approach:**
- Use match-level statistics (HY, HR, FTHG, FTAG) to create events
- Distribute goals across match minutes (randomly or by formation)
- Distribute yellow/red cards across players
- Add substitutions based on squad data

**Pros:**
- ✅ Uses existing data
- ✅ Quick to implement
- ✅ Populates table for analytics

**Cons:**
- ❌ Events are synthetic/simulated
- ❌ Not historically accurate
- ❌ Cannot know exact times or specific players

**Effort:** 2-3 hours

---

### Option 2: Acquire Event Data from External Source
Find and integrate real event-level data

**Sources:**
1. **Football-Data.org Premium API**
   - Requires paid subscription upgrade
   - Provides detailed event feeds
   - Most reliable option

2. **Understat / Wyscout / StatsBomb**
   - Advanced analytics platforms
   - Event data available (with licensing)
   - May be expensive

3. **Kaggle Datasets**
   - Search for "Premier League events" datasets
   - Often includes historical event-level data
   - Quality varies

4. **ESPN / Sky Sports APIs**
   - Some publicly available
   - May have terms-of-service restrictions

**Pros:**
- ✅ Real, accurate event data
- ✅ Includes all event types
- ✅ Trustworthy for analytics

**Cons:**
- ❌ May require cost/licensing
- ❌ Integration effort required
- ❌ Data available date range varies

**Effort:** 4-8 hours (depending on API documentation)

---

### Option 3: Manual CSV Import
Create or obtain CSV file with event-level data

**Format Expected:**
```csv
match_id,event_type,player_id,team_id,minute,extra_time
830_001,Goal,5678,1,15,0
830_001,Yellow Card,5679,1,23,0
830_001,Goal,5680,2,45,0
830_001,Red Card,5681,1,67,0
...
```

**Pros:**
- ✅ Simple to load
- ✅ Can validate manually
- ✅ One-time effort

**Cons:**
- ❌ Need to find/create the CSV
- ❌ Manual or one-time data collection
- ❌ Requires external data source

**Effort:** Depends on data availability

---

## Staging Table Structure Needed

If we implement Option 2 or 3, we need a staging table:

```sql
CREATE TABLE IF NOT EXISTS stg_match_events_raw (
    event_id VARCHAR(255) PRIMARY KEY,
    match_id INT,
    event_type VARCHAR(100),
    player_name VARCHAR(255),
    team_name VARCHAR(255),
    minute INT,
    extra_time INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'LOADED',
    raw_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX (match_id),
    INDEX (status)
);
```

---

## Recommended Path Forward

### Immediate (Week 1):
1. **Check football-data.org API documentation**
   ```
   Can we access /competitions/PL/matches/{id}/events endpoint?
   What's included in event data?
   What are subscription tier limitations?
   ```

2. **If NO event data available:**
   → Implement **Option 1 (Synthetic Events)** for development/demo
   - Creates realistic-looking events for analytics
   - Allows testing of fact_match_events queries
   - Can be replaced with real data later

3. **If YES event data available:**
   → Implement **Option 2 (API Integration)**
   - Add event extraction to `api_client.py`
   - Create `stg_match_events_raw` staging table
   - Build load script to populate `fact_match_events`

### Medium Term (Week 2-3):
- If using synthetic data, identify real event data source
- Test queries and analytics on populated fact_match_events
- Validate data quality and event distribution

### Long Term (Week 4+):
- Consider Understat or advanced analytics platform for more detailed events
- Implement real-time event ingestion for ongoing seasons

---

## Implementation Checklist

### For Synthetic Events (Quick Option):
- [ ] Create `src/etl/transform/generate_match_events.py`
- [ ] Algorithm: Distribute HY, HR, FTHG, FTAG across match timeline
- [ ] Create staging table `stg_match_events_raw`
- [ ] Create load script `src/sql/load_fact_match_events.sql`
- [ ] Test with sample matches
- [ ] Document data generation rules

### For Real Events (API Option):
- [ ] Check football-data.org API capabilities
- [ ] Extend `src/etl/extract/api_client.py` with event fetching
- [ ] Create staging table `stg_match_events_raw`
- [ ] Create manifest table `ETL_Events_Manifest`
- [ ] Create load script `src/sql/load_fact_match_events.sql`
- [ ] Implement error handling and retry logic
- [ ] Test with sample matches

---

## Data Quality Constraints

If we populate `fact_match_events`, these constraints must be maintained:

```sql
-- Foreign key integrity
- match_id MUST reference an existing record in fact_match
- player_id CAN be NULL (own goal, defensive action)
- team_id MUST reference an existing record in dim_team

-- Data validation
- minute MUST be >= 0 and <= 120
- event_type MUST be in allowed list (Goal, Yellow Card, Red Card, etc.)
- For each match: total goals from events SHOULD equal FTHG + FTAG
- For each match: total yellows from events SHOULD equal HY + AY
```

---

## Next Steps

**I need your direction:**

1. **Do you want synthetic/demo events?** → I can implement in 2-3 hours
2. **Do you want to check API capabilities first?** → Tell me to investigate football-data.org
3. **Do you have event data already?** → Share the file and I'll build the loader
4. **Skip this table for now?** → Focus on other analytics tables

Please choose and let me know how you'd like to proceed!
