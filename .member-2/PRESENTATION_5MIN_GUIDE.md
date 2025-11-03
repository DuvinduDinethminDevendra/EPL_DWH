# Member 2 Presentation - Database Schema Design
## 5-Minute Visual Presentation Guide

**Presenter:** Member 2 - Database Schema Designer  
**Time:** 5 minutes  
**Slides:** 6 slides

---

## 🎯 Slide 1: Title & Introduction (30 seconds)

### Title Slide
```
┌──────────────────────────────────────────────┐
│                                              │
│    EPL DATA WAREHOUSE                        │
│    Database Schema Design                    │
│                                              │
│    Member 2: [Your Name]                     │
│    Database Architect                        │
│                                              │
│    23 Tables | Fact Constellation            │
│    15+ Foreign Keys | 2.7M+ Rows             │
│                                              │
└──────────────────────────────────────────────┘
```

**What to say:**
> "Hi, I'm [Name], Member 2, and I designed the database schema - the foundation of our EPL Data Warehouse. I created 23 tables organized as a Fact Constellation pattern, with 15+ foreign key constraints ensuring data quality across 2.7 million rows."

---

## 📊 Slide 2: Schema Overview - The Big Picture (1 minute)

### Visual: 23 Tables Organization

```
┌─────────────────────────────────────────────────────────────┐
│            EPL DATA WAREHOUSE - 23 TABLES                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🗂️  DIMENSIONS (6)          📊 FACTS (3)                  │
│  Reference Data               Transactional Data           │
│  ├─ dim_date (17.5K)         ├─ fact_match (830)          │
│  ├─ dim_team (25)            ├─ fact_match_events (1.3M+) │
│  ├─ dim_player (6,847)       └─ fact_player_stats (1.6K)  │
│  ├─ dim_referee (32)                                       │
│  ├─ dim_stadium (25)         🔗 MAPPINGS (2)              │
│  └─ dim_season (7)           ├─ dim_team_mapping          │
│                               └─ dim_match_mapping         │
│  📝 AUDIT (6)                                              │
│  ETL Tracking                🏗️  STAGING (6)              │
│  ├─ ETL_Log                  Temporary Storage            │
│  ├─ ETL_File_Manifest        ├─ stg_e0_match_raw         │
│  ├─ ETL_Api_Manifest         ├─ stg_team_raw             │
│  ├─ ETL_Excel_Manifest       ├─ stg_player_raw           │
│  ├─ ETL_Events_Manifest      ├─ stg_player_stats_fbref   │
│  └─ ETL_JSON_Manifest        ├─ stg_referee_raw          │
│                               └─ stg_events_raw           │
└─────────────────────────────────────────────────────────────┘
```

**What to say:**
> "I organized 23 tables into 5 groups: 6 dimensions for reference data like teams and players, 3 fact tables for transactions and events, 2 mapping tables to bridge different data sources, 6 audit tables to track ETL operations, and 6 staging tables for temporary storage."

---

## 🔄 Slide 3: Fact Constellation Pattern (1 minute)

### Visual: Why Fact Constellation?

```
┌────────────────────────────────────────────────────────────┐
│         FACT CONSTELLATION SCHEMA PATTERN                  │
│         (Galaxy Schema - Multiple Perspectives)            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│              🌟 CONFORMED DIMENSIONS (6)                   │
│                                                            │
│     dim_date    dim_team    dim_player                    │
│     dim_referee  dim_stadium  dim_season                  │
│                                                            │
│                      ↓  ↓  ↓                              │
│         ┌────────────┼──┼──┼────────────┐                │
│         │            │  │  │            │                │
│    ┌────▼────┐  ┌───▼──▼──▼───┐  ┌────▼─────┐          │
│    │  MATCH  │  │   EVENTS    │  │  PLAYER  │          │
│    │  FACTS  │  │   FACTS     │  │  STATS   │          │
│    │         │  │             │  │  FACTS   │          │
│    │ 830 rows│  │1.3M+ rows   │  │1.6K rows │          │
│    │         │  │             │  │          │          │
│    │ Summary │  │  Detailed   │  │Individual│          │
│    │  Level  │  │   Events    │  │ Player   │          │
│    └─────────┘  └─────────────┘  └──────────┘          │
│                                                            │
│  ✅ Same dimensions = Consistent analysis                 │
│  ✅ Multiple facts = Multiple perspectives                │
│  ✅ Different levels = Flexible drill-down                │
└────────────────────────────────────────────────────────────┘
```

**What to say:**
> "I chose the Fact Constellation pattern because we need multiple perspectives. Instead of one fact table, we have three at different detail levels - match summaries, detailed events, and player statistics - all sharing the same 6 dimensions. This allows flexible analysis from match-level down to individual player actions."

---

## 📥 Slide 4: Data Sources → Staging → Dimensions (1 minute)

### Visual: Data Flow Part 1

```
┌─────────────────────────────────────────────────────────────────┐
│               DATA SOURCES TO STAGING TO DIMENSIONS             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 DATA SOURCES (4)         🏗️  STAGING (6)                   │
│  ┌────────────────┐          ┌──────────────────┐              │
│  │ StatsBomb JSON │──────────│stg_events_raw    │              │
│  │ 380 files      │          │1.3M+ events      │              │
│  │ 1.3M+ events   │          └──────────────────┘              │
│  └────────────────┘                  │                         │
│                                      │                         │
│  ┌────────────────┐          ┌──────▼───────────┐              │
│  │ CSV Files      │──────────│stg_e0_match_raw  │              │
│  │ E0 Season Data │          │830 matches       │              │
│  │ 830 matches    │          └──────────────────┘              │
│  └────────────────┘                  │                         │
│                                      │                         │
│  ┌────────────────┐          ┌──────▼───────────┐              │
│  │ API Calls      │──────────│stg_team_raw      │──────┐      │
│  │football-data.org          │stg_player_raw    │      │      │
│  │ Teams/Players  │          └──────────────────┘      │      │
│  └────────────────┘                  │                 │      │
│                                      │                 │      │
│  ┌────────────────┐          ┌──────▼───────────┐      │      │
│  │ Excel Files    │──────────│stg_referee_raw   │      │      │
│  │ Stadiums       │          │stg_player_stats  │      │      │
│  │ Referees       │          └──────────────────┘      │      │
│  └────────────────┘                  │                 │      │
│                                      │                 │      │
│                           TRANSFORM & CLEAN            │      │
│                                      │                 │      │
│                                      ▼                 ▼      │
│                          🗂️  DIMENSIONS (6)                   │
│                          ┌──────────────────┐                 │
│                          │ dim_date (17.5K) │                 │
│                          │ dim_team (25)    │                 │
│                          │ dim_player (6,847)                 │
│                          │ dim_referee (32) │                 │
│                          │ dim_stadium (25) │                 │
│                          │ dim_season (7)   │                 │
│                          └──────────────────┘                 │
│                                                                 │
│  ✅ Staging = Raw data buffer                                  │
│  ✅ Dimensions = Clean reference data                          │
└─────────────────────────────────────────────────────────────────┘
```

**What to say:**
> "Data flows through three stages. First, raw data from 4 sources loads into 6 staging tables. Then, my transformation logic cleans and loads 6 dimension tables with reference data like teams and players. The staging tables act as a buffer, allowing us to validate data before moving to final tables."

---

## 📊 Slide 5: Foreign Keys & Data Integrity (1 minute)

### Visual: Relationships & Constraints

```
┌─────────────────────────────────────────────────────────────────┐
│          FOREIGN KEY RELATIONSHIPS (15+ Constraints)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      🗂️  DIMENSIONS                            │
│        ┌──────────┬──────────┬──────────┬──────────┐          │
│        │ dim_date │ dim_team │dim_player│ dim_...  │          │
│        │   (PK)   │   (PK)   │   (PK)   │   (PK)   │          │
│        └────┬─────┴────┬─────┴────┬─────┴────┬─────┘          │
│             │ FK       │ FK       │ FK       │ FK              │
│             │          │          │          │                 │
│      ┌──────▼──────────▼──────────▼──────────▼─────┐          │
│      │         fact_match (830 rows)                │          │
│      │  ┌──────────────────────────────────┐        │          │
│      │  │ date_id (FK) → dim_date          │        │          │
│      │  │ season_id (FK) → dim_season      │        │          │
│      │  │ home_team_id (FK) → dim_team     │        │          │
│      │  │ away_team_id (FK) → dim_team     │        │          │
│      │  │ referee_id (FK) → dim_referee    │        │          │
│      │  │ stadium_id (FK) → dim_stadium    │        │          │
│      │  └──────────────────────────────────┘        │          │
│      │       │ match_id (PK)                        │          │
│      └───────┼──────────────────────────────────────┘          │
│              │ FK                                               │
│              │                                                  │
│      ┌───────▼─────────────────────────────────────┐          │
│      │   fact_match_events (1.3M+ rows)            │          │
│      │  ┌──────────────────────────────────┐       │          │
│      │  │ match_id (FK) → fact_match       │       │          │
│      │  │ player_id (FK) → dim_player      │       │          │
│      │  │ team_id (FK) → dim_team          │       │          │
│      │  └──────────────────────────────────┘       │          │
│      └──────────────────────────────────────────────┘          │
│                                                                 │
│  🔒 DATA INTEGRITY FEATURES:                                   │
│  ✅ 15+ Foreign Keys ensure relationships                      │
│  ✅ Primary Keys on all tables                                 │
│  ✅ Indexes on all FKs for fast joins                          │
│  ✅ Sentinel records (-1, 6808) for unknowns                   │
│  ✅ NOT NULL constraints on critical columns                   │
│  ✅ CHECK constraints (goals 0-20)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**What to say:**
> "I implemented 15+ foreign key constraints to ensure data integrity. Every fact record must reference valid dimensions. For example, fact_match has 6 foreign keys linking to date, season, teams, referee, and stadium. I also added indexes on all foreign keys for fast query performance, and sentinel records to handle missing data without breaking relationships."

---

## 🎯 Slide 6: Impact & Summary (30 seconds)

### Visual: Key Achievements

```
┌─────────────────────────────────────────────────────────────────┐
│              SCHEMA DESIGN - KEY ACHIEVEMENTS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 SCALE                        🔒 QUALITY                    │
│  ├─ 23 tables designed           ├─ 15+ FK constraints         │
│  ├─ 2.7M+ rows capacity          ├─ 100% referential integrity │
│  ├─ 4 data sources integrated    ├─ Zero data loss             │
│  └─ 6,847 players tracked        └─ Audit trail complete       │
│                                                                 │
│  🚀 PERFORMANCE                  🎯 FLEXIBILITY                 │
│  ├─ Indexes on all FKs           ├─ Fact Constellation pattern │
│  ├─ Optimized query paths        ├─ Multi-level analysis       │
│  ├─ Efficient joins              ├─ Match → Event → Player     │
│  └─ Fast aggregations            └─ Shared dimensions          │
│                                                                 │
│  💡 INNOVATION                   🤝 TEAM IMPACT                 │
│  ├─ Sentinel record strategy     ├─ Enabled Member 1 (ETL)     │
│  ├─ Manifest deduplication       ├─ Enabled Member 3 (Dims)    │
│  ├─ Mapping tables for IDs       ├─ Enabled Member 4 (Facts)   │
│  └─ Fact Constellation design    └─ Enabled Member 5 (BI)      │
│                                                                 │
│  ✅ RESULT: Solid, scalable foundation for the entire DWH      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**What to say:**
> "My schema design achieved four key goals: Scale - handling 2.7 million rows across 23 tables. Quality - 15+ foreign keys ensuring 100% data integrity. Performance - indexes enabling fast queries. And Flexibility - the Fact Constellation pattern allowing analysis from multiple perspectives. Most importantly, my foundation enabled all other team members to complete their work."

---

## 📝 Bonus: Q&A Preparation Slide

### Common Questions & Answers

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANTICIPATED Q&A                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Q: "Why Fact Constellation instead of Star Schema?"            │
│ A: "We need multiple perspectives - match summaries, detailed  │
│    events, and player stats - at different granularities.      │
│    Star schema only supports one fact table."                  │
│                                                                 │
│ Q: "What are sentinel records?"                                │
│ A: "Special records with ID -1 for unknown data. This          │
│    maintains referential integrity when data is missing."      │
│                                                                 │
│ Q: "How do you prevent duplicate data?"                        │
│ A: "I designed 6 audit tables with manifest systems that       │
│    track which files have been processed."                     │
│                                                                 │
│ Q: "Why 23 tables? Isn't that too many?"                       │
│ A: "Each serves a purpose: 6 dimensions, 3 facts, 2 mappings,  │
│    6 audit for tracking, 6 staging (temporary). This           │
│    separation ensures clean architecture."                     │
│                                                                 │
│ Q: "How does your schema support business queries?"            │
│ A: "Foreign keys enable complex joins, indexes speed up        │
│    queries, and Fact Constellation allows drilling from        │
│    match-level to event-level seamlessly."                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 How to Convert This to PowerPoint/Google Slides

### Method 1: Copy-Paste (Easiest)
1. Copy each slide's content
2. Paste into PowerPoint as **text**
3. Format with appropriate fonts (Consolas or Courier for diagrams)
4. Add colors to boxes/shapes

### Method 2: Use Diagrams (Better)
1. Use PowerPoint SmartArt for organizational charts
2. Use shapes and connectors for data flow
3. Use tables for the "23 Tables" overview
4. Screenshot ASCII diagrams if needed

### Method 3: Online Tools
1. **Draw.io** - Convert text diagrams to visual diagrams
2. **Mermaid Live Editor** - Create flowcharts from code
3. **Canva** - Create professional slides from templates

---

## ⏱️ Timing Breakdown

| Slide | Topic | Time | What to Show |
|-------|-------|------|--------------|
| 1 | Title & Intro | 30s | Title slide with key numbers |
| 2 | 23 Tables Overview | 1m | Table organization diagram |
| 3 | Fact Constellation | 1m | Pattern explanation visual |
| 4 | Data Flow | 1m | Sources → Staging → Dimensions |
| 5 | Foreign Keys | 1m | Relationships & integrity features |
| 6 | Impact & Summary | 30s | Achievement highlights |
| **Total** | | **5 min** | **6 slides** |

---

## 🎯 Speaker Notes for Each Slide

### Slide 1 - Opening Strong
- Make eye contact
- Speak confidently: "I designed the foundation"
- Emphasize numbers: 23 tables, 15+ FKs, 2.7M rows

### Slide 2 - Show Organization
- Point to each group of tables
- Explain purpose briefly
- "Everything has a place and purpose"

### Slide 3 - Pattern Explanation
- Use hand gestures: dimensions at top, facts below
- "Think of it like a solar system - dimensions are the sun, facts are planets"
- Emphasize "multiple perspectives"

### Slide 4 - Data Journey
- Trace the flow with your hand/pointer
- "Four sources → Six staging → Six dimensions"
- "Staging is the safety net"

### Slide 5 - Technical Depth
- Point to FK arrows
- "Every relationship is enforced"
- "This prevents bad data from entering"

### Slide 6 - Strong Finish
- Stand tall
- "My design enabled the entire team"
- "Questions?"

---

## 📸 Screenshot-Ready ASCII Art

You can take screenshots of these diagrams and paste directly into slides:

### Diagram 1: Simple Fact Constellation
```
        DIMENSIONS
    ┌─────────────────┐
    │ Date Team Player│
    │ Ref  Stadium... │
    └────┬────┬───┬────┘
         │    │   │
    ┌────▼────▼───▼────┐
    │   FACT TABLES    │
    │ Match Events Stats│
    └──────────────────┘
```

### Diagram 2: Data Flow
```
Sources → Staging → Transform → Dimensions
                              ↓
                         Fact Tables
```

### Diagram 3: Integrity
```
dim_team ──FK──> fact_match ──FK──> fact_match_events
   (PK)           (6 FKs)            (3 FKs)
```

---

## 🎤 Presentation Tips

1. **Practice timing**: Use a timer, aim for 4:30 to have buffer
2. **Use transitions**: "Moving to our next component..."
3. **Point to visuals**: Don't just read - reference the diagram
4. **Show confidence**: You designed this - own it!
5. **Pause for effect**: After key points, pause 2 seconds
6. **End with energy**: "Questions?" with a smile

---

## ✅ Final Checklist Before Presentation

- [ ] All 6 slides created in PowerPoint/Google Slides
- [ ] Diagrams are clear and readable
- [ ] Font size is large enough (min 18pt)
- [ ] Practiced full presentation 3+ times
- [ ] Timed at 4:30-5:00 minutes
- [ ] Prepared Q&A answers
- [ ] Confident about foreign keys explanation
- [ ] Can explain Fact Constellation in 30 seconds
- [ ] Know all table counts (23, 6, 3, 2, 6, 6)
- [ ] Ready to demo schema if asked

---

**Ready to create your PowerPoint?** Use these slides as your content guide!

**File to keep:** Save this as your presentation script  
**Next step:** Convert to PowerPoint/Google Slides  
**Backup:** Print this document as speaker notes

Good luck with your presentation! 🚀
