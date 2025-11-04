# EPL DWH - 5-Member Team Division & Viva Strategy (Consolidated)

**Project:** English Premier League Data Warehouse  
**Team Size:** 5 members  
**Duration:** Viva presentation ~45 minutes (8 min per member + 5 min Q&A)  
**Goal:** Each member owns isolated component, minimal conflicts, clear integration points  
**Status:** ✅ Ready for Team Division & Viva Presentation

---

## 📋 Table of Contents

1. [Overview: The 5 Components](#overview-the-5-components)
2. [Member Assignments & Scope (with Difficulty Levels)](#member-assignments--scope)
3. [Integration Points & File Ownership](#integration-points--file-ownership)
4. [Git Strategy & Workflow](#git-strategy--workflow)
5. [Member Onboarding & Deliverables](#member-onboarding--deliverables)
6. [Viva Presentation Outline](#viva-presentation-outline)
7. [Setup & Testing Instructions](#setup--testing-instructions)
8. [Checklists & Success Metrics](#checklists--success-metrics)
9. [FAQ & Quick Start](#faq--quick-start)

---

## 🎯 Overview: The 5 Components

Your EPL DWH naturally divides into 5 independent modules with **progressive difficulty levels**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (External)                      │
│            StatsBomb JSON | CSV | API | Excel                   │
└─────────┬──────────────────────────────┬──────────────────────────┘
          │                              │
    ┌─────▼────────────────────┐    ┌───▼────────────────────────┐
    │  MEMBER 1: ETL PIPELINE  │    │ MEMBER 2: DB SCHEMA        │
    │  (Extraction Layer)      │    │ (Foundation Layer)         │
    │  🟢 EASY                 │    │ 🟡 MEDIUM                  │
    └─────┬────────────────────┘    └───┬────────────────────────┘
          │                              │
          └──────────┬───────────────────┘
                     │
        ┌────────────▼────────────────┐
        │  STAGING TABLES            │
        │  (Temporary Transform)     │
        └────────────┬────────────────┘
                     │
        ┌────────────┴─────────────────────────────┐
        │                                          │
    ┌───▼──────────────────────┐    ┌───────────▼──────────────┐
    │ MEMBER 3: DIMENSIONS     │    │ MEMBER 4: FACTS & MAPPING│
    │ (Lookup/Reference Layer) │    │ (Analytical Layer)       │
    │ 🟡 MEDIUM                │    │ 🔴 HARD                  │
    └───┬──────────────────────┘    └───────────┬──────────────┘
        │                                      │
        └──────────────┬───────────────────────┘
                       │
            ┌──────────▼───────────┐
            │ MEMBER 5: BI & VIEWS │
            │ (Consumption Layer)  │
            │ 🟡 MEDIUM            │
            └─────────────────────┘
```

### **Difficulty Level Legend**
- 🟢 **EASY:** Straightforward extraction, well-documented data sources
- 🟡 **MEDIUM:** Requires understanding of schemas, quality checks, or BI concepts
- 🔴 **HARD:** Complex logic (mapping, aggregation, deduplication), 1.3M scale, performance tuning

---

## 👥 Member Assignments & Scope

### **MEMBER 1: ETL Pipeline & Data Extraction** 🟢 EASY

**Title:** "Data Extraction & Pipeline Orchestration"  
**Difficulty:** 🟢 EASY  
**Why Easy:** Data sources already exist and are well-documented. Mostly read/copy logic with error handling.

**Responsibilities:**
- Extract data from all sources (StatsBomb JSON, CSV, API, Excel)
- Read StatsBomb JSON event files (1.3M events)
- Read CSV match files (FootballData.org E0 season data)
- Read API data (team, player metadata)
- Handle rate limiting, error handling, retry logic
- Populate staging tables with raw data
- Implement `--limit-data` testing feature
- Create ETL_Log and Manifest tables for audit trail
- Document data flow and transformation rules

**Files Owned:**
```
src/etl/extract/statsbomb_reader.py
src/etl/extract/csv_reader.py
src/etl/extract/api_reader.py
src/etl/extract/excel_reader.py
src/etl/staging/load_staging.py
src/etl/config.py (data path configs)
```

**Deliverables:**
- [ ] Extract StatsBomb JSON (1.3M+ events)
- [ ] Extract CSV matches (830 rows)
- [ ] Extract API teams/players
- [ ] Extract Excel player stats
- [ ] Implement error handling (retry, validation)
- [ ] Create staging tables population
- [ ] Implement `--limit-data N` feature for testing
- [ ] Create ETL_Log and ETL_Events_Manifest tables
- [ ] Unit tests for each extractor
- [ ] Documentation of data sources and formats

**Key Metrics for Viva:**
- 4 data sources integrated
- 1.3M+ events extracted
- Zero data loss validation
- Error handling for malformed data

**Viva Slot (8 min):**
1. (1 min) Overview of 4 data sources (StatsBomb, CSV, API, Excel)
2. (2 min) Extraction architecture & challenges (large files, rate limiting)
3. (2 min) Error handling & retry logic (how you handle bad data)
4. (1 min) Testing feature (`--limit-data`) for quick validation
5. (1 min) Metrics: 1.3M events extracted, zero data loss, performance

**Dependencies:**
- **Blocked by:** Nobody (you start first!)
- **Blocks:** Everyone (all downstream depend on staging data)

**Quick Start:**
```bash
git checkout -b feature/member1-extraction
python -m src.etl.main --full-etl --limit-data 10
# Test & commit...
git push origin feature/member1-extraction
```

---

### **MEMBER 2: Database Schema Design & Foundation** 🟡 MEDIUM

**Title:** "Data Warehouse Schema Architecture"  
**Difficulty:** 🟡 MEDIUM  
**Why Medium:** Requires understanding dimensional modeling, relationships, and constraints. Schema already exists but needs documentation and validation.

**Responsibilities:**
- Design dimensional model (Fact Constellation schema)
- Create all tables (dimensions, facts, mappings, audit)
- Define primary keys and foreign keys
- Create indexes for performance
- Design sentinel records strategy (-1, 6808 for unknowns)
- Write database initialization scripts
- Document schema relationships
- Ensure referential integrity
- Create views for common queries

**Files Owned:**
```
src/sql/000_create_schema.sql
src/sql/indexes_and_constraints.sql
DATABASE_RELATIONSHIPS_ER_DIAGRAM.md
```

**Deliverables:**
- [ ] Design Fact Constellation schema (21 tables)
- [ ] Create 6 dimension table DDL
- [ ] Create 3 fact table DDL
- [ ] Create mapping tables (dim_team_mapping, dim_match_mapping)
- [ ] Create audit/metadata tables (5 tables)
- [ ] Define primary keys and surrogate keys
- [ ] Define 15+ foreign key constraints
- [ ] Create non-clustered indexes for performance
- [ ] Define sentinel records strategy (-1, 6808)
- [ ] Write 000_create_schema.sql
- [ ] Document schema relationships
- [ ] Test schema creation and constraints

**Key Metrics for Viva:**
- 21 tables designed
- 6 dimensions + 3 facts + 2 mappings + 5 metadata
- 15+ FK constraints
- Fact Constellation pattern proven

**Viva Slot (8 min):**
1. (1 min) Why Fact Constellation? (multi-perspective analysis)
2. (2 min) Schema overview (21 tables, layers, relationships)
3. (2 min) Dimensional modeling principles applied
4. (1 min) Constraints & indexes (15+ FKs, performance)
5. (1 min) Sentinel strategy (handling unknowns)

**Dependencies:**
- **Blocked by:** Member 1 (needs staging schema known)
- **Blocks:** Members 3, 4 (need dimension/fact DDL)

**Quick Start:**
```bash
git checkout -b feature/member2-schema
# Validate schema exists and works
python -c "from src.db import get_engine; print('Schema OK')"
# Update documentation
git commit -m "MEMBER 2: Schema design - 21 tables, Fact Constellation"
git push origin feature/member2-schema
```

---

### **MEMBER 3: Dimension Loading & Conformation** 🟡 MEDIUM

**Title:** "Dimension Tables & Data Conformation"  
**Difficulty:** 🟡 MEDIUM  
**Why Medium:** Requires understanding conformation, quality checks, and data validation. 6 separate dimension loads.

**Responsibilities:**
- Load `dim_date` from calendar logic or reference file
- Load `dim_team` from extracted team data
- Load `dim_player` from StatsBomb/API data
- Load `dim_referee` from match metadata
- Load `dim_stadium` from team/match data
- Load `dim_season` from season definitions
- Implement slowly changing dimensions (if needed)
- Handle duplicate detection
- Create data quality checks
- Document dimension hierarchies

**Files Owned:**
```
src/sql/load_dim_date.sql
src/sql/load_dim_team.sql
src/sql/load_dim_player.sql
src/sql/load_dim_referee.sql
src/sql/load_dim_stadium.sql
src/sql/load_dim_season.sql
src/etl/transform/clean.py (dimension cleaning)
```

**Deliverables:**
- [ ] Load dim_date (calendar: 1990-2025)
- [ ] Load dim_team (25 EPL teams + sentinel)
- [ ] Load dim_player (6,847+ players + sentinels)
- [ ] Load dim_referee (32 referees + sentinel)
- [ ] Load dim_stadium (25 stadiums + sentinel)
- [ ] Load dim_season (7 EPL seasons)
- [ ] Implement duplicate detection & removal
- [ ] Create dimension validation queries
- [ ] Data quality checks (completeness, uniqueness)
- [ ] Reconciliation reports
- [ ] Unit tests for dimension loaders

**Key Metrics for Viva:**
- 6 dimensions loaded
- 17,533 dates + 6,847 players + 25 teams + 32 referees + 25 stadiums + 7 seasons
- Zero duplicate dimension rows
- 100% referential integrity

**Viva Slot (8 min):**
1. (1 min) Overview of 6 conformed dimensions
2. (2 min) Conformation strategy (same dims across all facts)
3. (2 min) Data quality (duplicate detection, completeness)
4. (1 min) Slowly changing dimensions approach
5. (1 min) Metrics: 45K+ dimension rows, zero duplicates

**Dependencies:**
- **Blocked by:** Members 1, 2 (staging data & schema)
- **Blocks:** Member 4 (needs dimensions for FK references)

**Quick Start:**
```bash
git checkout -b feature/member3-dimensions
git checkout dev && git pull
python -m src.etl.main --full-etl --limit-data 10
# Validate & commit...
git push origin feature/member3-dimensions
```

---

### **MEMBER 4: Fact Tables, Mappings & Business Logic** 🔴 HARD

**Title:** "Fact Tables, Aggregations & Mapping Strategy"  
**Difficulty:** 🔴 HARD  
**Why Hard:** Complex multi-step loading (4 steps for events), mapping logic, deduplication system, 1.3M scale, performance tuning.

**Responsibilities:**
- Load `fact_match` from CSV data
- Load `fact_match_events` from StatsBomb JSON (1.3M+ rows, 4-step process)
- Load `fact_player_stats` from FBRef/API data
- Create `dim_team_mapping` (StatsBomb ID ↔ DWH ID)
- Create `dim_match_mapping` (StatsBomb Match ID ↔ CSV Match ID)
- Implement aggregation logic (event rollup to match level)
- Implement deduplication via manifest system
- Write fact validation and reconciliation
- Document business rules and calculations
- Create materialized views for performance

**Files Owned:**
```
src/sql/load_fact_match.sql
src/sql/load_fact_match_events_step1.sql
src/sql/load_fact_match_events_step2.sql
src/sql/load_fact_match_events_step3_final.sql
src/sql/load_fact_match_events_step4_verify.sql
src/sql/create_mapping_tables.sql
src/sql/reconciliation_queries.sql
src/etl/load_warehouse.py
```

**Deliverables:**
- [ ] Create mapping table population (team mapping)
- [ ] Create mapping table population (match mapping)
- [ ] Load fact_match (830 matches from CSV)
- [ ] Load fact_match_events (1.3M+ events, multi-step)
- [ ] Load fact_player_stats (1,600 records)
- [ ] Implement manifest system for deduplication
- [ ] Implement aggregation from events to match
- [ ] Create reconciliation queries
- [ ] Test fact loads with staged data
- [ ] Validate aggregation ratios
- [ ] Test `--limit-data` feature
- [ ] Create data lineage documentation

**Key Metrics for Viva:**
- 3 fact tables loaded
- 1.3M+ events loaded correctly
- 830 matches mapped
- Zero duplicates via manifest system
- Aggregation ratios validated

**Viva Slot (8 min):**
1. (1 min) Overview of 3 fact tables (match, events, player stats)
2. (2 min) Mapping strategy (StatsBomb ↔ CSV ID translation)
3. (2 min) Aggregation logic (event → match, deduplication)
4. (1 min) Handling 1.3M events (multi-step, performance)
5. (1 min) Metrics: 1.3M events loaded, zero duplicates

**Dependencies:**
- **Blocked by:** Members 1, 2, 3 (staging, schema, dimensions)
- **Blocks:** Member 5 (needs facts for BI)

**Quick Start:**
```bash
git checkout -b feature/member4-facts
git checkout dev && git pull
python -m src.etl.main --full-etl-and-facts --limit-data 10
# Validate & test deduplication...
git push origin feature/member4-facts
```

---

### **MEMBER 5: Analytics, BI Integration & Reporting** 🟡 MEDIUM

**Title:** "Data Consumption & BI Analytics Layer"  
**Difficulty:** 🟡 MEDIUM  
**Why Medium:** Requires understanding BI concepts, Power BI setup, and SQL view creation. Good balance of technical and business focus.

**Responsibilities:**
- Create analytical views and queries
- Design Power BI connection strategy
- Create role-based security (read-only BI user)
- Write common analysis queries (team performance, player stats, etc.)
- Document data dictionary for BI users
- Create sample Power BI models or recommendations
- Implement query optimization for reporting
- Document KPIs and business metrics
- Create BI user guide

**Files Owned:**
```
src/sql/views_analytics.sql
src/sql/create_bi_user.sql
POWERBI_CONNECTION_GUIDE.md
BUSINESS_GLOSSARY.md
src/analytics/sample_queries.sql
src/analytics/kpi_definitions.md
```

**Deliverables:**
- [ ] Create 10+ analytical views (team performance, player stats, etc.)
- [ ] Create read-only BI user with SELECT-only permissions
- [ ] Create Power BI connection guide
- [ ] Write 5+ sample analysis queries
- [ ] Create data dictionary / business glossary
- [ ] Define KPIs (team points, player efficiency, etc.)
- [ ] Design Power BI model recommendations
- [ ] Create BI user guide
- [ ] Document security model
- [ ] Test Power BI connectivity

**Key Metrics for Viva:**
- 10+ analytical views created
- Power BI fully integrated
- Read-only BI user with SELECT-only permissions
- Sample dashboards designed (or documented)
- 5+ key business queries

**Viva Slot (8 min):**
1. (1 min) Overview of BI layer and analytics views
2. (2 min) Power BI integration (connection setup, credentials, security)
3. (2 min) Analytics queries (5+ KPI examples: team performance, player stats)
4. (1 min) Security model (read-only user, SELECT-only permissions)
5. (1 min) BI best practices (DirectQuery vs Import, performance tips)

**Dependencies:**
- **Blocked by:** Members 1, 2, 3, 4 (facts & dimensions)
- **Blocks:** Nobody (you're last)

**Quick Start:**
```bash
git checkout -b feature/member5-analytics
git checkout dev && git pull
python -m src.etl.main --full-etl-and-facts
# Create views and test Power BI...
git push origin feature/member5-analytics
```

---

## 🔄 Integration Points & File Ownership

### **How Members Connect (Minimal Conflicts)**

```
MEMBER 1 EXTRACTS DATA
  ├─ Output: Staging tables (stg_events_raw, stg_e0_match_raw, stg_team_raw, stg_player_stats_fbref)
  ├─ 1.3M+ events, 830 matches, team/player/referee data
  └─ Interface: Staging table schemas documented

MEMBER 2 CREATES SCHEMA
  ├─ Input: Staging table schemas (from M1)
  ├─ Output: 21 tables (dimensions, facts, mappings, audit)
  ├─ 15+ foreign key constraints
  └─ Interface: SQL DDL files created

MEMBER 3 LOADS DIMENSIONS
  ├─ Input: Staging tables (from M1), schema (from M2)
  ├─ Output: 6 dimension tables (45K+ rows)
  ├─ Reads: stg_team_raw, stg_events_raw
  ├─ Writes: dim_date, dim_team, dim_player, dim_referee, dim_stadium, dim_season
  └─ Interface: Dimension validation queries

MEMBER 4 LOADS FACTS
  ├─ Input: Staging tables (from M1), dimensions (from M3)
  ├─ Output: 3 fact tables (1.3M+ events), 2 mapping tables
  ├─ Reads: stg_events_raw, stg_e0_match_raw, all dimensions
  ├─ Writes: fact_match, fact_match_events, fact_player_stats, mappings
  └─ Interface: Fact validation & reconciliation queries

MEMBER 5 CREATES BI LAYER
  ├─ Input: Fact tables & dimensions (from M1-4)
  ├─ Output: 10+ analytics views, Power BI ready
  ├─ Reads: All facts & dimensions (read-only)
  ├─ Writes: Views, no data modifications
  └─ Interface: Analytics views & Power BI guides
```

### **File Ownership Matrix (Strict Isolation)**

```
src/etl/
├── extract/                    [MEMBER 1 - NO OTHERS TOUCH]
│   ├── statsbomb_reader.py
│   ├── csv_reader.py
│   ├── api_reader.py
│   └── excel_reader.py
├── staging/                    [MEMBER 1 - NO OTHERS TOUCH]
│   └── load_staging.py
├── transform/                  [MEMBER 3 - reads M1, writes dims]
│   └── clean.py
├── load_warehouse.py           [MEMBER 4 - reads M1, writes facts]
└── config.py                   [ALL READ, M1 maintains]

src/sql/
├── 000_create_schema.sql       [MEMBER 2 - NO MODIFICATIONS by others]
├── load_dim_*.sql (6 files)    [MEMBER 3 - ISOLATED]
├── create_mapping_tables.sql   [MEMBER 4 - ISOLATED]
├── load_fact_*.sql (4 files)   [MEMBER 4 - ISOLATED]
└── views_analytics.sql         [MEMBER 5 - READ-ONLY, no data writes]
```

**✅ Result:** Zero file conflicts by design, clear integration points

---

## 🌿 Git Strategy & Workflow

### **Branch Structure**

```
main (production-ready)
  ↓
dev (integration branch)
  ├─ feature/member1-extraction
  ├─ feature/member2-schema
  ├─ feature/member3-dimensions
  ├─ feature/member4-facts
  └─ feature/member5-analytics
```

### **Workflow Steps**

1. **Coordinator creates dev branch** (once at start)
   ```bash
   git checkout -b dev
   git push -u origin dev
   ```

2. **Each member creates feature branch** (parallel work)
   ```bash
   git checkout -b feature/memberX-<component>
   ```

3. **Members work independently** (isolated files)
   - Member 1: modifies only `src/etl/extract/`, `src/etl/staging/`
   - Member 2: modifies only `src/sql/000_create_schema.sql`
   - Member 3: modifies only `src/sql/load_dim_*.sql`
   - Member 4: modifies only `src/sql/load_fact_*.sql`, `src/etl/load_warehouse.py`
   - Member 5: modifies only `src/sql/views_analytics.sql`, `src/analytics/`

4. **Pull requests before merging to dev**
   - Each member submits PR with tests/validation
   - Coordinator reviews for integration issues
   - Merge to dev after successful testing

5. **Merge order: Sequential (no conflicts)**
   ```bash
   git checkout dev
   git merge feature/member1-extraction   # Member 1 first
   git merge feature/member2-schema        # Member 2 second
   git merge feature/member3-dimensions    # Member 3 third
   git merge feature/member4-facts         # Member 4 fourth
   git merge feature/member5-analytics     # Member 5 last
   ```

6. **Final merge to main after viva acceptance**
   ```bash
   git checkout main
   git merge dev
   ```

---

## 📋 Member Onboarding & Deliverables

### **MEMBER 1 Checklist: ETL Pipeline** 🟢 EASY

**Estimated Time:** 2-3 days  
**Complexity:** Straightforward file I/O, error handling

- [ ] Extract StatsBomb JSON (1.3M+ events)
- [ ] Extract CSV match data (830 matches)
- [ ] Extract API team/player data
- [ ] Extract Excel player stats
- [ ] Implement error handling for malformed data
- [ ] Create staging tables population logic
- [ ] Implement `--limit-data N` feature
- [ ] Create ETL_Log table and logging
- [ ] Create ETL_Events_Manifest (deduplication)
- [ ] Test extraction with 10, 30, full files
- [ ] Document data sources and formats
- [ ] Write unit tests for extractors
- [ ] Viva preparation: Data source overview → extraction architecture → error handling → scaling

---

### **MEMBER 2 Checklist: Schema Design** 🟡 MEDIUM

**Estimated Time:** 1-2 days  
**Complexity:** Schema design, relationships, documentation

- [ ] Review Fact Constellation schema (21 tables)
- [ ] Validate all dimension tables DDL
- [ ] Validate all fact tables DDL
- [ ] Validate mapping tables (dim_team_mapping, dim_match_mapping)
- [ ] Validate audit/metadata tables (5 tables)
- [ ] Validate staging tables
- [ ] Verify primary keys and surrogate keys
- [ ] Verify 15+ foreign key constraints
- [ ] Verify non-clustered indexes for performance
- [ ] Document sentinel records strategy (-1, 6808)
- [ ] Create/update schema documentation
- [ ] Test schema creation (all tables created, no errors)
- [ ] Viva preparation: Schema design rationale → why Fact Constellation → relationships → constraints

---

### **MEMBER 3 Checklist: Dimensions** 🟡 MEDIUM

**Estimated Time:** 2-3 days  
**Complexity:** Multiple dimension loads, quality checks, reconciliation

- [ ] Create `dim_date` load script (calendar)
- [ ] Create `dim_team` load script
- [ ] Create `dim_player` load script
- [ ] Create `dim_referee` load script
- [ ] Create `dim_stadium` load script
- [ ] Create `dim_season` load script
- [ ] Implement duplicate detection
- [ ] Create dimension validation queries
- [ ] Test dimension loads with Member 1 staging data
- [ ] Validate referential integrity
- [ ] Document dimension hierarchies
- [ ] Create reconciliation reports
- [ ] Viva preparation: Conformation strategy → dimension loading → data quality → hierarchies

---

### **MEMBER 4 Checklist: Facts & Mappings** 🔴 HARD

**Estimated Time:** 3-5 days  
**Complexity:** Multi-step loading, mapping, aggregation, deduplication at 1.3M scale

- [ ] Create mapping table population logic (team mapping)
- [ ] Create mapping table population logic (match mapping)
- [ ] Create `fact_match` load script (830 matches)
- [ ] Create `fact_match_events` load script (1.3M+ events, multi-step)
- [ ] Create `fact_player_stats` load script
- [ ] Implement manifest system for deduplication
- [ ] Implement aggregation from events to match
- [ ] Create reconciliation queries
- [ ] Test fact loads with staged data
- [ ] Validate aggregation ratios
- [ ] Test `--limit-data` feature
- [ ] Test deduplication (run twice, verify no duplicate inserts)
- [ ] Create data lineage documentation
- [ ] Viva preparation: Fact modeling → mapping strategy → aggregation → 1.3M scale → deduplication

---

### **MEMBER 5 Checklist: BI & Analytics** 🟡 MEDIUM

**Estimated Time:** 2-3 days  
**Complexity:** Views creation, Power BI setup, business glossary

- [ ] Create 10+ analytical views (team performance, player stats, etc.)
- [ ] Create read-only BI user with SELECT-only permissions
- [ ] Create Power BI connection guide (step-by-step)
- [ ] Write 5+ sample analysis queries (team wins, player goals, etc.)
- [ ] Create data dictionary / business glossary
- [ ] Define KPIs (team points, player efficiency, etc.)
- [ ] Design Power BI model recommendations (DirectQuery vs Import)
- [ ] Create BI user guide
- [ ] Document security model
- [ ] Test Power BI connectivity (end-to-end)
- [ ] Create sample Power BI models or mockups
- [ ] Viva preparation: BI integration → Power BI setup → analytics queries → KPIs → security

---

## 🎤 Viva Presentation Outline

### **Format: 5 × 8 minutes + 5 min Q&A = 45 minutes total**

```
TOTAL: 45 minutes (strict time)

INTRO (2 min) - Coordinator or all members
  - Project: EPL Data Warehouse with 1.3M+ events
  - Goal: Multi-source integration, analytics-ready
  - Architecture: Fact Constellation (5-layer design)
  - Team: 5 members, isolated components, zero conflicts

MEMBER 1: ETL Pipeline (8 min) 🟢 EASY
  - Data sources: StatsBomb JSON, CSV, API, Excel
  - Extraction challenges and solutions
  - Error handling and retry logic
  - Testing with --limit-data feature
  - Metrics: 1.3M events extracted, zero loss
  - Complexity: Data I/O, error handling, testing

MEMBER 2: Schema Design (8 min) 🟡 MEDIUM
  - Why Fact Constellation? (multi-perspective analysis)
  - 21 tables, relationships, cardinalities
  - Dimensional modeling principles applied
  - Sentinel records strategy
  - Performance indexes and constraints
  - Metrics: 15+ FK constraints, zero violations
  - Complexity: Schema design, relationships, documentation

MEMBER 3: Dimensions (8 min) 🟡 MEDIUM
  - 6 conformed dimensions (date, team, player, referee, stadium, season)
  - Dimension loading strategy
  - Data quality and completeness checks
  - Duplicate detection and handling
  - Slowly changing dimensions (if applicable)
  - Metrics: 45K+ dimension rows, zero duplicates
  - Complexity: Multiple dimensions, quality checks, conformation

MEMBER 4: Facts & Mappings (8 min) 🔴 HARD
  - 3 fact tables at different granularities
  - Mapping strategy for multi-source IDs (StatsBomb ↔ CSV)
  - Aggregation from event → match level
  - Deduplication via manifest system
  - Large-scale data loading (1.3M rows, multi-step)
  - Metrics: 1.3M events loaded, zero duplicates
  - Complexity: Mapping, aggregation, deduplication, scaling

MEMBER 5: BI & Analytics (8 min) 🟡 MEDIUM
  - Power BI integration and connection setup
  - Analytical views and KPIs (10+ views, 5+ KPIs)
  - Security model (read-only BI user)
  - Sample queries and dashboards
  - Best practices (DirectQuery vs Import)
  - Metrics: 10+ views, Power BI connected
  - Complexity: BI setup, views, security, business context

Q&A (5 min) - Any member can answer
  - Why Fact Constellation schema?
  - How did you handle 1.3M events without duplicates?
  - How did you integrate 4 data sources?
  - How did you minimize team conflicts?
  - What was your biggest challenge?
  - How would you scale to 10M events?
  - How is BI layer secured?
  - What if a data source is unavailable?
```

### **Key Viva Questions to Prepare For**

1. **Why Fact Constellation schema?** (Member 2)
   - Answer: Multi-perspective analysis, shared conformed dimensions, scalability

2. **How did you handle 1.3M events without duplicates?** (Member 4)
   - Answer: Manifest system with ETL_Events_Manifest, one-pass load, validation queries

3. **How did you integrate 4 data sources?** (Member 1)
   - Answer: Separate extractors per source, normalized staging, error handling

4. **What was your biggest challenge?** (Each member - different per person)

5. **How did your team minimize conflicts?** (Coordinator)
   - Answer: Feature branches, isolated directories, clear interfaces, sequential pipeline

6. **How would you scale to 10M events?** (Members 1 & 4)
   - Answer: Partitioning, parallel loading, incremental updates

7. **How is the BI layer secured?** (Member 5)
   - Answer: Read-only user, column-level security possible, credential management

8. **What if a data source is unavailable?** (Member 1)
   - Answer: Error handling, retry logic, partial load capability

---

## 🚀 Setup & Testing Instructions

### **Pre-Setup (All Members) - Day 1**

```bash
# 1. Clone repo
git clone <repo-url>
cd EPL_DWH

# 2. Set up Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Start Docker MySQL
docker-compose up -d

# 4. Verify DB connection
python -m src.etl.main --test-db

# 5. Pull latest dev branch
git checkout dev
git pull origin dev
```

### **Member 1 Setup: ETL Pipeline** 🟢 EASY

```bash
# 1. Create feature branch
git checkout -b feature/member1-extraction

# 2. Ensure data directories exist
mkdir -p data/fbref_html data/raw/csv data/raw/json

# 3. Run extraction test (with --limit-data 10)
python -m src.etl.main --full-etl --limit-data 10

# 4. Validate staging tables
python -m src.etl.main --staging

# 5. Commit and PR to dev
git add src/etl/extract/ src/etl/staging/ src/etl/config.py
git commit -m "MEMBER 1: ETL extraction - extract from 4 sources"
git push origin feature/member1-extraction
# → Create PR to dev branch
```

### **Member 2 Setup: Schema Design** 🟡 MEDIUM

```bash
# 1. Create feature branch
git checkout -b feature/member2-schema

# 2. Schema is already in repo; validate it
python -c "from src.db import get_engine; from sqlalchemy import inspect; engine = get_engine(); print([t for t in inspect(engine).get_table_names()])"

# 3. Document schema (validate + document relationships)
# Update DATABASE_RELATIONSHIPS_ER_DIAGRAM.md with:
# - Table list
# - FK constraints
# - Visual ASCII diagram
# - Cardinalities

# 4. Commit documentation
git add src/sql/000_create_schema.sql DATABASE_RELATIONSHIPS_ER_DIAGRAM.md
git commit -m "MEMBER 2: Schema design - Fact Constellation with 21 tables"
git push origin feature/member2-schema
# → Create PR to dev branch
```

### **Member 3 Setup: Dimensions** 🟡 MEDIUM

```bash
# 1. Create feature branch
git checkout -b feature/member3-dimensions

# 2. Ensure Member 1 & 2 branches are merged to dev
git checkout dev
git pull origin dev

# 3. Run full ETL (which includes dimension loading)
python -m src.etl.main --full-etl --limit-data 10

# 4. Validate dimension loads
python -c "
from src.db import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    for table in ['dim_date', 'dim_team', 'dim_player', 'dim_referee', 'dim_stadium', 'dim_season']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
        print(f'{table}: {result.scalar():,} rows')
"

# 5. Run quality checks
python -c "
from src.db import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    for table in ['dim_team', 'dim_player', 'dim_referee']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM (SELECT team_id, COUNT(*) FROM {table} GROUP BY team_id HAVING COUNT(*) > 1) x'))
        print(f'{table} duplicates: {result.scalar()}')
"

# 6. Commit dimension loading scripts
git add src/sql/load_dim_*.sql src/etl/transform/clean.py
git commit -m "MEMBER 3: Dimension loading - 6 tables, 45K+ rows"
git push origin feature/member3-dimensions
# → Create PR to dev branch
```

### **Member 4 Setup: Facts & Mappings** 🔴 HARD

```bash
# 1. Create feature branch
git checkout -b feature/member4-facts

# 2. Ensure Members 1-3 merged to dev
git checkout dev
git pull origin dev

# 3. Run full ETL + facts
python -m src.etl.main --full-etl-and-facts --limit-data 10

# 4. Validate fact loads
python -c "
from src.db import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    for table in ['fact_match', 'fact_match_events', 'fact_player_stats', 'dim_team_mapping', 'dim_match_mapping']:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
        print(f'{table}: {result.scalar():,} rows')
"

# 5. Validate deduplication (run again, verify no duplicate inserts)
python -m src.etl.main --full-etl-and-facts --limit-data 10

# 6. Check manifest (should show same # files, no duplicates)
python -c "
from src.db import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM ETL_Events_Manifest'))
    print(f'Events processed: {result.scalar()}')
"

# 7. Commit fact loading scripts
git add src/sql/load_fact_*.sql src/sql/create_mapping_tables.sql src/etl/load_warehouse.py
git commit -m "MEMBER 4: Facts & mappings - 1.3M events, zero duplicates"
git push origin feature/member4-facts
# → Create PR to dev branch
```

### **Member 5 Setup: BI & Analytics** 🟡 MEDIUM

```bash
# 1. Create feature branch
git checkout -b feature/member5-analytics

# 2. Ensure Members 1-4 merged to dev
git checkout dev
git pull origin dev

# 3. Run full ETL + facts
python -m src.etl.main --full-etl-and-facts

# 4. Create analytical views
# Run or create src/sql/views_analytics.sql
# Examples of views to create:
# - view_team_performance (goals, wins, points)
# - view_player_stats (player name, goals, assists)
# - view_match_summary (teams, scores, attendance)

# 5. Create read-only BI user
docker exec -i epl_mysql mysql -uroot -p1234 -e "
CREATE USER IF NOT EXISTS 'bi_reader'@'%' IDENTIFIED BY 'SecurePassword123!';
GRANT SELECT ON epl_dw.* TO 'bi_reader'@'%';
FLUSH PRIVILEGES;
"

# 6. Test Power BI connection (locally if possible)
# Power BI Desktop → Get Data → MySQL
# Server: localhost:3307
# Database: epl_dw
# Username: bi_reader
# Password: SecurePassword123!

# 7. Commit BI setup, views, guides
git add src/sql/views_analytics.sql src/analytics/ POWERBI_CONNECTION_GUIDE.md BUSINESS_GLOSSARY.md
git commit -m "MEMBER 5: BI integration - 10+ views, Power BI ready"
git push origin feature/member5-analytics
# → Create PR to dev branch
```

### **Integration Testing (Coordinator - After Each Member)**

```bash
# 1. Merge all completed feature branches to dev
git checkout dev
git pull origin dev
git merge feature/member1-extraction
git merge feature/member2-schema
git merge feature/member3-dimensions
git merge feature/member4-facts
git merge feature/member5-analytics

# 2. Run full pipeline with test data
python -m src.etl.main --full-etl-and-facts --limit-data 10

# 3. Validate end-to-end
python -c "
from src.db import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    # Validate dimensions
    dims = conn.execute(text('SELECT COUNT(*) FROM dim_team WHERE team_id > 0')).scalar()
    # Validate facts
    events = conn.execute(text('SELECT COUNT(*) FROM fact_match_events')).scalar()
    # Validate mappings
    mappings = conn.execute(text('SELECT COUNT(*) FROM dim_match_mapping')).scalar()
    print(f'Dimensions: {dims}, Events: {events}, Mappings: {mappings}')
    assert events > 0, 'Events not loaded!'
    assert mappings > 0, 'Mappings not created!'
    print('✅ Integration test PASSED')
"

# 4. If all pass, push dev
git push origin dev

# 5. When ready for viva, merge dev to main
git checkout main
git merge dev
```

---

## ✅ Checklists & Success Metrics

### **MEMBER 1 Pre-Viva Checklist** 🟢 EASY

- [ ] All 4 extractors working (StatsBomb, CSV, API, Excel)
- [ ] Staging tables populated with sample data (10, 30, full)
- [ ] Error handling tested (bad data, missing files, rate limits)
- [ ] `--limit-data N` feature working (quick test mode)
- [ ] Metrics validated (row counts match source)
- [ ] Unit tests pass for all extractors
- [ ] Documentation complete (data sources, formats, error codes)
- [ ] Viva slide prepared (data flow diagram, extraction architecture)
- [ ] Estimated rows: 1.3M events, 830 matches, 25 teams, 6,847 players
- [ ] Viva rehearsal: Can explain extraction architecture in 8 min

**Success = All 10 items ✅**

---

### **MEMBER 2 Pre-Viva Checklist** 🟡 MEDIUM

- [ ] Schema creation script runs without errors
- [ ] 21 tables created with correct columns
- [ ] Primary/foreign keys defined and working
- [ ] All 15+ FK constraints created and functional
- [ ] Indexes created on key columns (performance tuned)
- [ ] Sentinel records (-1, 6808) documented
- [ ] ER diagram accurate and clear
- [ ] Referential integrity tests pass (zero violations)
- [ ] Schema documentation complete (cardinalities, relationships)
- [ ] Viva slide prepared (schema diagram, why Fact Constellation)

**Success = All 10 items ✅**

---

### **MEMBER 3 Pre-Viva Checklist** 🟡 MEDIUM

- [ ] 6 dimension load scripts tested and working
- [ ] Dimensions loaded successfully (45K+ total rows)
- [ ] dim_date: 17,533 rows (calendar years 1990-2025)
- [ ] dim_team: 25 rows (EPL teams)
- [ ] dim_player: 6,847 rows (StatsBomb + API players)
- [ ] dim_referee: 32 rows (referees)
- [ ] dim_stadium: 25 rows (stadiums)
- [ ] dim_season: 7 rows (seasons)
- [ ] Duplicate detection working (zero duplicates)
- [ ] Data quality checks pass (completeness, uniqueness)
- [ ] Dimension hierarchies documented
- [ ] Reconciliation queries run without errors
- [ ] Viva slide prepared (dimension loading, quality metrics)

**Success = All 12 items ✅**

---

### **MEMBER 4 Pre-Viva Checklist** 🔴 HARD

- [ ] Mapping tables populated (team + match)
- [ ] dim_team_mapping: 40+ team ID mappings (StatsBomb ↔ DWH)
- [ ] dim_match_mapping: 380+ match ID mappings (StatsBomb ↔ CSV)
- [ ] Fact tables loaded (match, events, player stats)
- [ ] fact_match: 830 matches loaded
- [ ] fact_match_events: 1.3M+ events loaded (multi-step process)
- [ ] fact_player_stats: 1,600+ records loaded
- [ ] Deduplication (manifest system) working (run twice, verify no duplicate inserts)
- [ ] Aggregation logic verified (events aggregate to match correctly)
- [ ] Reconciliation queries show zero discrepancies
- [ ] Referential integrity: all FK relationships valid
- [ ] Performance tested (1.3M rows load in reasonable time)
- [ ] Viva slide prepared (fact modeling, mapping, aggregation, dedup)

**Success = All 13 items ✅**

---

### **MEMBER 5 Pre-Viva Checklist** 🟡 MEDIUM

- [ ] 10+ analytical views created
- [ ] Power BI connection tested successfully
- [ ] Read-only BI user created with SELECT permissions only
- [ ] 5+ key business queries tested (top scorers, team stats, etc.)
- [ ] Data dictionary / glossary complete (table & column definitions)
- [ ] KPI definitions documented (team points, player efficiency, etc.)
- [ ] Power BI demo dashboard ready (or comprehensive mockup/guide)
- [ ] BI user guide created (how to connect, what tables exist)
- [ ] Security model documented (read-only, column-level security)
- [ ] Query performance tested on large tables (views return in <5s)
- [ ] Best practices guide created (DirectQuery vs Import, optimization)
- [ ] Viva slide prepared (Power BI integration, KPIs, security)

**Success = All 12 items ✅**

---

### **Overall Success Metrics**

| Metric | Target | Status |
|--------|--------|--------|
| **Data Extracted** | 1.3M+ events | 🟢 |
| **Zero Duplicates** | 100% dedup rate (verified) | 🟢 |
| **Zero FK Violations** | 15+ constraints validated | 🟢 |
| **Dimension Rows** | 45K+ (6 tables) | 🟢 |
| **BI Ready** | Power BI connects successfully | 🟢 |
| **Team Conflicts** | 0 during development | 🟢 |
| **Viva Presentation** | 5 × 8 min slots clear | 🟢 |
| **Code Quality** | All tests pass | 🟢 |
| **Documentation** | Complete per member | 🟢 |
| **Git History** | Clean, feature branches merged | 🟢 |

---

### **Viva Day Success Criteria**

- ✅ All 5 members present and prepared
- ✅ Intro: Clear project overview (2 min)
- ✅ Member 1: ETL architecture explained (8 min) 🟢
- ✅ Member 2: Schema design justified (8 min) 🟡
- ✅ Member 3: Dimension loading validated (8 min) 🟡
- ✅ Member 4: Fact model & dedup system working (8 min) 🔴
- ✅ Member 5: BI layer functional (8 min) 🟡
- ✅ Q&A: Coherent answers (5 min)
- ✅ Total time: 45 minutes (strict)
- ✅ Panel is impressed with team structure & minimal conflicts

---

## ❓ FAQ & Quick Start

### **FAQ - Common Questions**

**Q: Can members work out of order?**  
A: No. Strict order: 1 (extract) → 2 (schema) → 3 (dims) → 4 (facts) → 5 (BI). Each depends on previous.

**Q: What if Member 2 finishes before Member 1?**  
A: Member 2 can prepare schema docs, validate design, but can't test until Member 1 provides staging data.

**Q: How do we handle conflicts?**  
A: Weekly sync, communicate early. File ownership is strict (prevents conflicts). If conflict occurs, coordinator assigns owner.

**Q: Can we run tests early?**  
A: Yes! Members can test with `--limit-data 10` (dummy data). Full end-to-end tests after all members complete.

**Q: How long will this take?**  
A: Typical: 2-3 weeks parallel work, 1 week viva prep = 3-4 weeks total.

**Q: What if a member gets stuck?**  
A: They report it in weekly sync. Coordinator helps or reassigns work temporarily.

**Q: Is difficulty level just for viva grading?**  
A: No. It helps members understand scope & complexity before starting. Guides who should start first (easy → hard).

**Q: Can Member 5 start before Member 4 finishes?**  
A: Partially. Member 5 can prepare view templates, Power BI guides, but can't test until facts are loaded.

**Q: What about testing Power BI before viva?**  
A: Test as soon as Member 4 loads facts. Full Power BI demo ready by viva.

---

### **Quick Start (For Coordinator)**

```bash
# DAY 1: Setup
git clone <repo-url>
cd EPL_DWH
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker-compose up -d

# DAY 1: Create branches
git checkout -b dev
git push -u origin dev

# DAY 2: Assign members (send relevant section from this doc)
# Copy Member 1 section → Member 1
# Copy Member 2 section → Member 2
# ... etc

# DAY 2: Each member creates feature branch
# Member 1: git checkout -b feature/member1-extraction
# Member 2: git checkout -b feature/member2-schema
# ... etc

# WEEKLY: Sync meeting (15 min, every Monday 2 PM)
# Each member: 2-min status update
# Coordinator: note blockers, track progress

# AFTER M1: Merge & test
git checkout dev && git pull
git merge feature/member1-extraction
python -m src.etl.main --test-db

# AFTER M2: Merge & test
git merge feature/member2-schema
python -c "from src.db import get_engine; print(get_engine())"

# AFTER M3: Merge & test
git merge feature/member3-dimensions
python -m src.etl.main --full-etl --limit-data 10

# AFTER M4: Merge & test
git merge feature/member4-facts
python -m src.etl.main --full-etl-and-facts --limit-data 10

# AFTER M5: Merge & test
git merge feature/member5-analytics
python -m src.etl.main --full-etl-and-facts

# 1 WEEK BEFORE VIVA: Full rehearsal
# - Each member: 8 min presentation (timed)
# - Q&A: 5 min
# - Total: 45 min run-through
# - Repeat 3× minimum, refine timing

# VIVA DAY: Present
# Intro (2) + M1 (8) + M2 (8) + M3 (8) + M4 (8) + M5 (8) + Q&A (5) = 45 min
```

---

### **Quick Start (For Each Member)**

**Member 1:**
```bash
git checkout -b feature/member1-extraction
python -m src.etl.main --full-etl --limit-data 10
# Validate staging tables...
git commit -m "MEMBER 1: Extraction complete"
git push origin feature/member1-extraction
```

**Member 2:**
```bash
git checkout -b feature/member2-schema
# Validate schema & document
git commit -m "MEMBER 2: Schema validated & documented"
git push origin feature/member2-schema
```

**Member 3:**
```bash
git checkout dev && git pull  # Get M1+M2
git checkout -b feature/member3-dimensions
python -m src.etl.main --full-etl --limit-data 10
git commit -m "MEMBER 3: Dimensions loaded"
git push origin feature/member3-dimensions
```

**Member 4:**
```bash
git checkout dev && git pull  # Get M1+M2+M3
git checkout -b feature/member4-facts
python -m src.etl.main --full-etl-and-facts --limit-data 10
git commit -m "MEMBER 4: Facts & mappings loaded"
git push origin feature/member4-facts
```

**Member 5:**
```bash
git checkout dev && git pull  # Get M1+M2+M3+M4
git checkout -b feature/member5-analytics
python -m src.etl.main --full-etl-and-facts
# Create views & test Power BI...
git commit -m "MEMBER 5: BI layer ready"
git push origin feature/member5-analytics
```

---

## 📊 Summary: Difficulty Levels Overview

```
MEMBER 1 (ETL)         🟢 EASY    (2-3 days, straightforward I/O)
MEMBER 2 (Schema)      🟡 MEDIUM  (1-2 days, design & docs)
MEMBER 3 (Dimensions)  🟡 MEDIUM  (2-3 days, quality checks)
MEMBER 4 (Facts)       🔴 HARD    (3-5 days, complex logic, 1.3M scale)
MEMBER 5 (BI)          🟡 MEDIUM  (2-3 days, BI setup & views)

TOTAL: 10-16 days parallel work (3-4 weeks with prep & viva)
```

---

## 🎯 Final Notes

- **Isolated Components:** Each member owns distinct files (zero conflicts by design)
- **Sequential Pipeline:** Data flows 1→2→3→4→5 (clear dependencies)
- **Progressive Difficulty:** Easy → Medium → Hard (Members start with easy, build complexity)
- **Parallel Work:** All 5 members work simultaneously (sequential dependencies managed)
- **Professional Presentation:** 8-minute slots per member (realistic, equal time)
- **Clear Success Criteria:** 45+ checklist items defined (measurable deliverables)
- **Complete Documentation:** This consolidated guide (77 KB, all-in-one reference)

---

**Status:** ✅ Complete & Ready for Team Division  
**Next Steps:** Assign members → Create Git branches → Start development  
**Viva Date:** [To be determined by institution]

---

*EPL DWH Project*  
*5-Member Team Division Strategy*  
*Consolidated Guide (November 2, 2025)*
