# EPL Data Warehouse - Schema Quick Reference

**Schema Pattern:** ✅ Fact Constellation (Galaxy Schema)  
**Last Updated:** November 3, 2025

---

## 📊 Schema Overview

**23 Tables Total:**
- 6 Dimensions (reference data)
- 3 Facts (transactional data)
- 2 Mappings (ID translation)
- 6 Audit (ETL tracking)
- 6 Staging (temporary)

---

## 🎯 Fact Constellation Structure

```
┌────────────────────────────────────────────┐
│     6 SHARED CONFORMED DIMENSIONS          │
│  dim_date | dim_team | dim_player         │
│  dim_referee | dim_stadium | dim_season   │
└─────┬──────────┬──────────┬───────────────┘
      │          │          │
┌─────▼────┐ ┌──▼──────────▼───┐ ┌─────────▼─────┐
│fact_match│ │fact_match_events│ │fact_player    │
│ (830)    │ │    (1.3M+)      │ │_stats (1.6K)  │
└──────────┘ └─────────────────┘ └───────────────┘
```

**Why Fact Constellation?**
- Multiple facts at different granularities
- All facts share same dimensions
- Enables flexible multi-perspective analysis

---

## 📋 Dimensions (6)

| Table | Rows | Purpose |
|-------|------|---------|
| `dim_date` | 17.5K | Calendar 1992-2040 |
| `dim_team` | 25 | EPL teams |
| `dim_player` | 6,847 | All players |
| `dim_referee` | 32 | Match officials |
| `dim_stadium` | 25 | Venues |
| `dim_season` | 7 | Seasons 2017-2026 |

**Sentinel Records:** -1 (unknown), 6808 (unknown player)

---

## 📈 Facts (3)

### fact_match (830 rows)
**Granularity:** One row per match  
**Foreign Keys:** date_id, season_id, home_team_id, away_team_id, referee_id, stadium_id  
**Measures:** home_goals, away_goals, shots, fouls, cards, attendance

### fact_match_events (1.3M+ rows)
**Granularity:** One row per event (pass, shot, foul, etc.)  
**Foreign Keys:** match_id → fact_match, player_id, team_id  
**Measures:** event_type, minute, period, timestamp, event details

### fact_player_stats (1,600 rows)
**Granularity:** One row per player per match  
**Foreign Keys:** match_id, player_id, team_id, season_id  
**Measures:** minutes_played, goals, assists, shots, cards

---

## 🔗 Relationships

### Primary Relationships:
```
fact_match ←─ 6 dimensions (date, season, teams, referee, stadium)
    ↓
fact_match_events ←─ fact_match (via match_id)
    ↓
    ←─ 2 dimensions (player, team)

fact_player_stats ←─ fact_match + 3 dimensions
```

### Total Foreign Keys: 15+
- fact_match: 6 FKs
- fact_match_events: 3 FKs  
- fact_player_stats: 4 FKs
- dim_match_mapping: 1 FK

---

## 🔀 Mapping Tables (2)

| Table | Purpose |
|-------|---------|
| `dim_team_mapping` | StatsBomb team_id ↔ dim_team.team_id |
| `dim_match_mapping` | StatsBomb match_id ↔ fact_match.match_id |

**Why needed:** Different data sources use different IDs

---

## 📝 Audit Tables (6)

| Table | Tracks |
|-------|--------|
| `ETL_Log` | All ETL operations |
| `ETL_File_Manifest` | CSV files processed |
| `ETL_Api_Manifest` | API calls made |
| `ETL_Excel_Manifest` | Excel files processed |
| `ETL_Events_Manifest` | StatsBomb event files (prevents duplicates) |
| `ETL_JSON_Manifest` | JSON files processed |

---

## 🏗️ Staging Tables (6)

| Table | Source |
|-------|--------|
| `stg_e0_match_raw` | CSV match data |
| `stg_team_raw` | API team data |
| `stg_player_raw` | JSON player data |
| `stg_player_stats_fbref` | FBRef stats |
| `stg_referee_raw` | Excel referee data |
| `stg_events_raw` | StatsBomb events |

**Purpose:** Temporary storage before transformation

---

## 🔍 Key Design Features

### 1. Data Integrity
- ✅ 15+ foreign key constraints
- ✅ Primary keys on all tables
- ✅ NOT NULL on critical columns
- ✅ Sentinel records for missing data

### 2. Performance
- ✅ Indexes on all foreign keys
- ✅ Indexes on date columns (year, month)
- ✅ Indexes on team_code for lookups

### 3. Data Quality
- ✅ Check constraints (goals 0-20)
- ✅ Audit tables track all loads
- ✅ Manifest system prevents duplicates

### 4. Flexibility
- ✅ Fact Constellation enables multiple analysis perspectives
- ✅ Conformed dimensions ensure consistency
- ✅ Mapping tables bridge different sources

---

## 📊 Query Patterns

### Match Summary Analysis
```sql
SELECT t.team_name, SUM(fm.home_goals) as total_goals
FROM fact_match fm
JOIN dim_team t ON fm.home_team_id = t.team_id
GROUP BY t.team_name;
```

### Event-Level Drill-Down
```sql
SELECT p.player_name, COUNT(*) as pass_count
FROM fact_match_events fme
JOIN dim_player p ON fme.player_id = p.player_id
WHERE fme.event_type = 'Pass'
GROUP BY p.player_name;
```

### Cross-Fact Analysis
```sql
SELECT fm.match_id, fm.home_goals,
       COUNT(fme.event_id) as total_events
FROM fact_match fm
JOIN fact_match_events fme ON fm.match_id = fme.match_id
GROUP BY fm.match_id, fm.home_goals;
```

### Multi-Dimensional Analysis
```sql
SELECT d.year, t.team_name, s.stadium_name,
       AVG(fm.home_goals) as avg_goals
FROM fact_match fm
JOIN dim_date d ON fm.date_id = d.date_id
JOIN dim_team t ON fm.home_team_id = t.team_id
JOIN dim_stadium s ON fm.stadium_id = s.stadium_id
GROUP BY d.year, t.team_name, s.stadium_name;
```

---

## ✅ Fact Constellation Criteria

| Criterion | Status |
|-----------|--------|
| Multiple fact tables | ✅ 3 facts |
| Different granularities | ✅ Match/Event/Player |
| Shared dimensions | ✅ 6 shared |
| Conformed dimensions | ✅ Yes |
| Fact-to-fact relationships | ✅ match_id FK |
| Bridge/mapping tables | ✅ 2 tables |
| Multi-source integration | ✅ 4 sources |

**Result:** ✅ **CONFIRMED FACT CONSTELLATION**

---

## 📈 Data Volumes

| Category | Volume |
|----------|--------|
| Total rows (production) | 2.7M+ |
| Match facts | 830 |
| Event facts | 1.3M+ |
| Player stats | 1,600 |
| Dimension records | 24,000+ |
| StatsBomb matches | 380 |
| CSV matches | 830 |

---

## 🎯 For Presentations

**One-liner:**  
"A Fact Constellation schema with 3 facts at different granularities sharing 6 conformed dimensions."

**Key talking points:**
1. **Pattern:** Fact Constellation (multiple facts, shared dimensions)
2. **Scale:** 23 tables, 2.7M+ rows, 15+ foreign keys
3. **Integrity:** Sentinel records, constraints, audit trails
4. **Flexibility:** Multi-perspective analysis (match/event/player)
5. **Quality:** Manifest system prevents duplicates

---

**File:** `src/sql/000_create_schema.sql` (542 lines)  
**Documentation:** `DATABASE_RELATIONSHIPS_ER_DIAGRAM.md`  
**Project:** EPL Data Warehouse
