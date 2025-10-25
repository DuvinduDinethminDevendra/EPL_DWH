# StatsBomb Event Data Integration - LIVE EXTRACTION

**Status:** ⏳ IN PROGRESS (27% complete)

**Extracted So Far:**
- ✓ 398,307 events loaded
- ✓ 113 matches completed
- ✓ ~27% of 418 EPL matches
- ⏱ Estimated completion: 4-5 minutes

## Process Overview

### 1. Repository Setup
✓ Downloaded StatsBomb open-data ZIP from GitHub
✓ Extracted to `data/raw/open-data-master/`
✓ Verified 3464 event JSON files available
✓ Identified 418 unique EPL matches (seasons 2003-04 and 2015-16)

### 2. Event Data Structure
```
data/raw/open-data-master/
└── data/
    ├── competitions.json
    ├── matches/
    │   └── 2/  (Premier League, competition_id=2)
    │       ├── 27.json (2015-16: 380 matches)
    │       └── 44.json (2003-04: 38 matches)
    └── events/
        └── <match_id>.json (3464 files total)
```

### 3. Event Fields Extracted
Per-match JSON files contain arrays of events with:
- **Event Identification**: event_id, type, timestamp, minute, second, period
- **Actor Information**: player_name, player_id, team_name, team_id, position
- **Context**: possession_team_name, play_pattern, tactics_formation
- **Action-Specific Data**:
  - Pass: recipient_name, pass_length, carry_end_location
  - Shot: outcome, xG (expected goals)
  - Duel: outcome
- **Raw Data**: Full JSON stored for audit

### 4. Staging Schema
**stg_events_raw** table (53 columns):
- Primary key: event_id (StatsBomb-unique)
- Foreign key: statsbomb_match_id (links to fact_match)
- All fields nullable except keys
- status column for ETL tracking
- Indexed on: statsbomb_match_id, type, player_name, team_name, status

**ETL_Events_Manifest** table (load audit):
- statsbomb_match_id
- file_name, file_path
- load_start_time, load_end_time
- status (SUCCESS/ERROR), rows_processed

### 5. Event Type Distribution
Top 15 event types in sample load:
- Pass: 8,505
- Ball Receipt*: 7,858
- Carry: 7,000
- Pressure: 2,031
- Ball Recovery: 666
- Duel: 425
- Block: 261
- Clearance: 249
- Dribble: 242
- Goal Keeper: 219
- Foul Committed: 208
- Foul Won: 199
- Shot: 193
- Interception: 185
- Miscontrol: 181

### 6. Performance Metrics
- Parse + bulk insert rate: ~3,500 events/second
- Database write: ~500 rows/commit (using pandas.to_sql method="multi")
- Match processing: ~3-4 seconds per match (4000 events avg)
- Manifest recording: Immediate post-insert

### 7. Next Steps (After Extraction Completes)
1. ✓ Verify final event counts
2. ✓ Transform stg_events_raw → fact_match_events (load_fact_match_events.sql)
3. ✓ Validate dimensional joins (match_id, player_id, team_id)
4. ✓ Data quality checks (missing dimensions, orphaned records)
5. ✓ Update ETL audit logs

---

**Live Status Updates:**
- [17:35:08] 113 matches, 398,307 events - 27% complete
- [ETA] 17:39-17:40 (remaining time ~4-5 min)
