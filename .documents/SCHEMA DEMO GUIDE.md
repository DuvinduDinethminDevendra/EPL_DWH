# 🎯 Member 2's Demonstration Guide
## Mapping Your Role to University Evaluation Guidelines

**Date:** November 2, 2025  
**Course:** ICT 3233 Mini Project  
**Your Role:** Member 2 - Database Schema Designer  
**Demonstration Time:** 20-25 minutes (total team), ~4-5 minutes (your part)

---

## 📋 Quick Answer to Your Questions

### Q1: "Is my guide aligned with the demonstration requirements?"
**Answer:** ✅ **YES!** Your guide covers everything you need, BUT you need to understand which parts of the demonstration guidelines YOU are responsible for.

### Q2: "What does '15 business queries' mean?"
**Answer:** The 15 business queries can be demonstrated in **THREE ways**:
1. ✅ **SQL queries** - Write and run SQL in MySQL (most common)
2. ✅ **Power BI dashboards** - Show visualizations that answer business questions
3. ✅ **Mix of both** - Some SQL queries + some Power BI visuals

**For your team:** Member 5 is primarily responsible for this section (they handle BI & Analytics). But YOU might contribute 2-3 queries showing how your schema enables analysis.

---

## 🎓 Complete Demonstration Requirements Breakdown

### 1️⃣ **Introduction** (2-3 minutes - WHOLE TEAM)

**What the guidelines ask for:**
- ✓ Introduce the organization/business
- ✓ Describe purpose of the data warehouse

**Your team's answer:**
- **Organization:** English Premier League (EPL)
- **Purpose:** Store and analyze football match data (1.3M+ events, 830 matches) to help coaches, analysts, and fans make data-driven decisions

**Your contribution (Member 2):**
- 🟡 **Minor role** - Just listen or mention you designed the database structure
- One sentence: "I designed the schema that stores all this data efficiently"

---

### 2️⃣ **Development Platform** (2 minutes - MEMBER 1 or PROJECT LEAD)

**What the guidelines ask for:**
- ✓ Describe the data warehousing tool used
- ✓ Explain reasons for selection

**Your team's answer:**
- **Tool:** MySQL 8.0 (relational database)
- **Reasons:**
  - Free and open-source
  - Handles large volumes (1.3M+ rows)
  - Strong referential integrity (foreign keys)
  - Good performance with indexes
  - Easy to connect with Python ETL and Power BI

**Your contribution (Member 2):**
- 🟢 **MAJOR ROLE!** - YOU explain why MySQL was chosen for the schema
- Mention: "MySQL supports foreign keys and constraints which are essential for data quality in my schema design"

---

### 3️⃣ **Project Overview** (8-10 minutes - MULTIPLE MEMBERS)

This is THE BIGGEST section and involves MULTIPLE members. Let's break it down:

#### **Part A: Conceptual Schema** (Member 2 - YOUR MAIN PART!)

**What the guidelines ask for:**
- ✓ Explain the conceptual schema of the data warehouse

**Your contribution (Member 2):**
- 🟢 🟢 🟢 **THIS IS YOUR STAR MOMENT!** (3-4 minutes)

**What to explain:**
1. **Schema Pattern:** "We use a Fact Constellation schema"
   - Show diagram (dimensions = sun, facts = planets)
   - Explain why: "Multiple perspectives on the same data"

2. **The 23 Tables:**
   - 6 Dimensions (reference data)
   - 3 Facts (transactions/events)
   - 2 Mappings (ID translation)
   - 6 Audit tables (tracking)
   - 6 Staging tables (temporary storage)

3. **Show the ER Diagram:**
   - Display: `DATABASE_RELATIONSHIPS_ER_DIAGRAM.md`
   - Point out: Foreign key relationships
   - Explain: "All fact tables connect to the same dimensions"

4. **Key Design Decisions:**
   - "We use sentinel records (-1, 6808) for unknown data"
   - "15+ foreign keys ensure data integrity"
   - "Indexes on key columns for fast queries"

**Time:** 3-4 minutes  
**Slides/Visuals:** ER diagram, table list, Fact Constellation diagram

---

#### **Part B: Source and Destination Tables** (Member 1 + Member 2)

**What the guidelines ask for:**
- ✓ Explain source and destination tables
- ✓ Explain what data is in these tables

**Split responsibility:**

**Member 1 explains SOURCES:**
- **Source tables (staging):**
  - `stg_e0_match_raw` - Raw CSV match data (830 matches)
  - `stg_events_raw` - Raw StatsBomb events (1.3M rows)
  - `stg_team_raw` - Raw team data from API
  - `stg_player_raw` - Raw player data
  - `stg_referee_raw` - Raw referee data
  - `stg_player_stats_fbref` - Raw player statistics

**Member 2 (YOU) explains DESTINATIONS:**
- **Destination tables (final warehouse):**
  
  **Dimensions (reference data):**
  - `dim_date` - Calendar dates (17,500 rows)
  - `dim_team` - 25 EPL teams
  - `dim_player` - 6,847 players
  - `dim_referee` - 32 referees
  - `dim_stadium` - 25 stadiums
  - `dim_season` - 7 seasons
  
  **Facts (analysis data):**
  - `fact_match` - 830 match summaries
  - `fact_match_events` - 2.6M individual events (passes, shots, goals)
  - `fact_player_stats` - Player performance metrics

**Your talking points:**
- "Source tables hold raw, uncleaned data"
- "Destination tables hold cleaned, structured data ready for analysis"
- "My schema ensures destination tables have proper relationships"

**Time:** 2 minutes (1 min Member 1, 1 min you)

---

#### **Part C: Data Loading Process** (Member 3 + Member 4)

**What the guidelines ask for:**
- ✓ Show how data loads from source to destination

**Your contribution (Member 2):**
- 🟡 **Supporting role** - Just mention:
  - "The schema I designed ensures data can flow smoothly"
  - "Foreign keys validate data during loading"

**Main speakers:** Members 3 & 4 (they handle the actual ETL execution)

**Time:** 1-2 minutes (mostly others)

---

#### **Part D: Data Refreshing Period** (Member 4 or Project Lead)

**What the guidelines ask for:**
- ✓ Describe data refreshing period
- ✓ Update target tables or delete and reload?

**Your team's answer:**
- **Refresh strategy:** Full reload (delete and load again)
- **Frequency:** On-demand (run when new data available)
- **Why:** Clean slate ensures no duplicates
- **Protection:** Manifest tables track what's been processed

**Your contribution (Member 2):**
- 🟡 **Minor role** - Just mention:
  - "My schema supports both incremental and full reloads"
  - "The audit tables I designed track each data load"

**Time:** 1 minute (mostly others)

---

### 4️⃣ **Business Queries and Results** (8-10 minutes - MEMBER 5 leads, but YOU contribute)

**What the guidelines ask for:**
- ✓ Develop 15 meaningful business queries
- ✓ Show results of 15 queries
- ✓ Highlight importance for business

**🎯 UNDERSTANDING "15 BUSINESS QUERIES":**

A business query is a question that helps the business make decisions. It can be shown in **three ways**:

#### **Option 1: SQL Queries (Most Common)**
Write SQL and show results in a table:

```sql
-- Query 1: Which team scored the most goals at home in 2024?
SELECT 
    t.team_name,
    SUM(fm.home_goals) as total_goals
FROM fact_match fm
JOIN dim_team t ON fm.home_team_id = t.team_id
JOIN dim_date d ON fm.date_id = d.date_id
WHERE d.year = 2024
GROUP BY t.team_name
ORDER BY total_goals DESC
LIMIT 5;
```

#### **Option 2: Power BI Dashboards**
Create visualizations that answer questions:
- Bar chart: "Top 5 Goal Scorers in 2024"
- Line chart: "Manchester United's Performance Over Time"
- Map: "Goals by Stadium Location"

#### **Option 3: Mixed Approach** ✅ RECOMMENDED
- 10 queries shown as SQL with results
- 5 queries shown as Power BI visuals

**Your team should do:** Mix of both (most flexible for 20-minute demo)

---

### **Your Specific Contribution to Business Queries (Member 2):**

**Your responsibility:** Contribute **2-3 queries** that showcase your SCHEMA DESIGN

**Your queries should demonstrate:**
1. ✅ Foreign key relationships working
2. ✅ Multiple tables joining correctly
3. ✅ Fact Constellation pattern in action

**Example Queries YOU Should Present:**

#### **Query 1: Show Fact Constellation in Action**
"This query demonstrates how our Fact Constellation design allows us to analyze across multiple fact tables:"

```sql
-- Show how many events happened in high-scoring matches
SELECT 
    fm.match_id,
    t_home.team_name as home_team,
    t_away.team_name as away_team,
    fm.home_goals + fm.away_goals as total_goals,
    COUNT(fme.event_id) as total_events
FROM fact_match fm
JOIN fact_match_events fme ON fm.match_id = fme.match_id
JOIN dim_team t_home ON fm.home_team_id = t_home.team_id
JOIN dim_team t_away ON fm.away_team_id = t_away.team_id
GROUP BY fm.match_id
HAVING total_goals >= 5
ORDER BY total_goals DESC;
```

**Your explanation:** "This query shows how fact_match and fact_match_events work together, connected through my schema's foreign keys."

#### **Query 2: Show Dimensional Modeling**
"This demonstrates how dimensions provide context to facts:"

```sql
-- Player performance across different stadiums and referees
SELECT 
    p.player_name,
    s.stadium_name,
    r.referee_name,
    COUNT(fme.event_id) as total_actions,
    SUM(CASE WHEN fme.event_type = 'Shot' THEN 1 ELSE 0 END) as shots
FROM fact_match_events fme
JOIN dim_player p ON fme.player_id = p.player_id
JOIN fact_match fm ON fme.match_id = fm.match_id
JOIN dim_stadium s ON fm.stadium_id = s.stadium_id
JOIN dim_referee r ON fm.referee_id = r.referee_id
WHERE p.player_name = 'Mohamed Salah'
GROUP BY p.player_name, s.stadium_name, r.referee_name
ORDER BY total_actions DESC;
```

**Your explanation:** "This shows how conformed dimensions (player, stadium, referee) all connect to provide rich analysis context."

#### **Query 3: Show Data Integrity (Sentinel Records)**
"This demonstrates our sentinel record strategy handling missing data:"

```sql
-- Show matches where referee or stadium was unknown
SELECT 
    fm.match_id,
    t_home.team_name as home_team,
    t_away.team_name as away_team,
    r.referee_name,
    s.stadium_name,
    CASE 
        WHEN fm.referee_id = -1 THEN 'Unknown Referee'
        WHEN fm.stadium_id = -1 THEN 'Unknown Stadium'
        ELSE 'Complete Data'
    END as data_quality_status
FROM fact_match fm
JOIN dim_team t_home ON fm.home_team_id = t_home.team_id
JOIN dim_team t_away ON fm.away_team_id = t_away.team_id
JOIN dim_referee r ON fm.referee_id = r.referee_id
JOIN dim_stadium s ON fm.stadium_id = s.stadium_id
WHERE fm.referee_id = -1 OR fm.stadium_id = -1;
```

**Your explanation:** "My schema uses sentinel records (-1) to maintain referential integrity even when data is missing."

---

### **Division of 15 Business Queries Among Team:**

**Suggested split:**
- **Member 2 (YOU):** 2-3 queries showing schema design
- **Member 3:** 3-4 queries on dimension data quality
- **Member 4:** 3-4 queries on fact data and aggregations
- **Member 5:** 5-6 queries with Power BI visuals

**Total:** 15+ queries covering all aspects

---

### 5️⃣ **Contribution of Team Members** (3-4 minutes - EVERYONE)

**What the guidelines ask for:**
- ✓ All members participate
- ✓ Each member describes their contribution

**Your contribution statement (Member 2):**

**What to say (1 minute):**

> "Hi, I'm [Your Name], Member 2, and I was responsible for **Database Schema Design**.
> 
> **My main contributions were:**
> 
> 1. **Designed the Fact Constellation schema** - 23 tables organized into 6 dimensions, 3 facts, 2 mappings, 6 audit tables, and 6 staging tables.
> 
> 2. **Ensured data integrity** - Implemented 15+ foreign key constraints to prevent invalid data entry and maintain referential integrity.
> 
> 3. **Created the foundation** - My schema design enables all other team members to work. Member 1 loads data into my staging tables, Member 3 populates my dimension tables, Member 4 fills my fact tables, and Member 5 queries my schema for analysis.
> 
> 4. **Implemented smart design patterns** - Used sentinel records (-1, 6808) to handle missing data, created indexes for fast queries, and designed the Fact Constellation pattern to allow analysis from multiple perspectives.
> 
> **Files I worked on:**
> - `src/sql/000_create_schema.sql` (542 lines - creates all 23 tables)
> - `DATABASE_RELATIONSHIPS_ER_DIAGRAM.md` (documentation)
> 
> **Impact:** Without my schema, the data warehouse wouldn't exist. I provided the foundation that everyone else built upon."

**Time:** 1 minute

---

## 📊 Your Exact Responsibilities - Checklist

### Before Demonstration:

#### **Documents to Prepare:**
- [ ] ER Diagram (print or slide) - show table relationships
- [ ] Fact Constellation diagram - show design pattern
- [ ] Table list with row counts - show 23 tables
- [ ] 2-3 SQL queries showcasing schema design
- [ ] Schema explanation slides (3-4 slides)

#### **What to Memorize:**
- [ ] "23 tables total: 6 dimensions, 3 facts, 2 mappings, 6 audit, 6 staging"
- [ ] "Fact Constellation pattern - multiple facts share dimensions"
- [ ] "15+ foreign keys ensure data integrity"
- [ ] "Sentinel records (-1, 6808) handle missing data"

#### **Practice:**
- [ ] Explain Fact Constellation in 1 minute
- [ ] Show ER diagram and explain in 2 minutes
- [ ] Run your 2-3 SQL queries and explain results
- [ ] Describe your contribution in 1 minute

---

### During Demonstration:

| Section | Your Role | Time | What to Show |
|---------|-----------|------|--------------|
| **1. Introduction** | 🟡 Minor | 30 sec | Mention you designed the schema |
| **2. Development Platform** | 🟢 Major | 1 min | Explain why MySQL for schema |
| **3A. Conceptual Schema** | 🟢🟢🟢 **STAR!** | 3-4 min | ER diagram, Fact Constellation, 23 tables |
| **3B. Source/Destination** | 🟢 Major | 1 min | Explain destination tables you designed |
| **3C. Data Loading** | 🟡 Minor | 30 sec | Mention schema enables smooth loading |
| **3D. Data Refreshing** | 🟡 Minor | 30 sec | Mention audit tables you designed |
| **4. Business Queries** | 🟢 Major | 2-3 min | Present 2-3 queries, explain schema role |
| **5. Your Contribution** | 🟢🟢 Major | 1 min | Summarize your work |

**Total speaking time for you:** ~8-10 minutes (out of 20-25 total)

---

## 🎯 Alignment with Your Guide

### Does MEMBER2_BEGINNERS_GUIDE.md cover demonstration requirements?

| Demonstration Requirement | Covered in Your Guide? | Section Reference |
|---------------------------|------------------------|-------------------|
| Explain conceptual schema | ✅ YES | Part 6 (Fact Constellation), Part 3 (23 tables) |
| Show ER diagram | ✅ YES | Part 6, Part 10 (relationships) |
| Explain source/destination | ✅ YES | Part 3 (table groups) |
| Schema design decisions | ✅ YES | Part 7 (sentinel records, constraints) |
| Your contribution | ✅ YES | Part 9 (viva presentation) |
| Business queries | 🟡 PARTIAL | Part 11 shows example queries, but you need to create YOUR 2-3 specific ones |

**Overall:** ✅ **95% aligned!** Your guide gives you all the knowledge. You just need to:
1. Create 2-3 specific SQL queries for demo
2. Prepare visual diagrams/slides
3. Practice your 8-10 minute speaking parts

---

## 🎓 Action Items - What to Do NOW

### Week 1: Preparation (This Week)

**Day 1-2: Create Visual Materials**
- [ ] Create ER diagram (can use draw.io or PowerPoint)
- [ ] Create Fact Constellation diagram
- [ ] Create table summary slide (23 tables breakdown)

**Day 3-4: Prepare Your Queries**
- [ ] Write 2-3 SQL queries (use examples from this guide)
- [ ] Test queries in MySQL
- [ ] Take screenshots of results
- [ ] Prepare explanation for each query

**Day 5-6: Create Presentation Slides**
- [ ] Slide 1: "I'm Member 2 - Schema Designer"
- [ ] Slide 2: Fact Constellation explanation
- [ ] Slide 3: ER diagram
- [ ] Slide 4: 23 tables breakdown
- [ ] Slide 5: Query results

**Day 7: Practice**
- [ ] Practice explaining schema in 3-4 minutes
- [ ] Practice running queries and explaining
- [ ] Practice your contribution statement (1 minute)
- [ ] Time yourself (should be 8-10 minutes total)

### Week 2: Team Coordination

**Day 1: Team Meeting**
- [ ] Coordinate with Member 5 on business queries (who does which?)
- [ ] Agree on demo flow (who speaks when?)
- [ ] Share your slides with team

**Day 2-3: Full Team Practice**
- [ ] Do a complete 20-25 minute run-through
- [ ] Get feedback from team
- [ ] Adjust timing if needed

**Day 4-5: Final Prep**
- [ ] Memorize key numbers (23 tables, 15+ FKs, etc.)
- [ ] Practice smooth transitions between speakers
- [ ] Prepare for Q&A (common questions about schema)

---

## 💡 Common Questions You Might Get

### During Demonstration Q&A:

**Q1: "Why did you choose Fact Constellation over Star Schema?"**
**Your answer:** "Star schema has one fact table. We have 3 fact tables (matches, events, player stats) at different granularities. Fact Constellation allows us to analyze from multiple perspectives while sharing the same dimensions for consistency."

**Q2: "What happens if data is missing for a referee or stadium?"**
**Your answer:** "We use sentinel records with ID -1 for unknown values. This maintains referential integrity—foreign keys still point to valid records, but we know the data is incomplete."

**Q3: "How do you prevent duplicate data?"**
**Your answer:** "We have 6 audit tables that track which files and data sources have been processed. The ETL_Events_Manifest table specifically prevents duplicate event loading."

**Q4: "Why 23 tables? Isn't that too many?"**
**Your answer:** "Each table has a specific purpose. 6 are temporary staging tables (deleted after ETL), 6 are audit/tracking tables, 6 are dimensions, 3 are facts, and 2 are mappings. This separation ensures clean data architecture."

**Q5: "How does your schema support the 15 business queries?"**
**Your answer:** "My schema enables complex analysis through: 1) Conformed dimensions that connect all facts, 2) Foreign keys that ensure data accuracy, 3) Indexes on key columns for fast queries, and 4) The Fact Constellation pattern that allows drilling down from match-level to event-level."

---

## 📝 Final Checklist - Before Demonstration Day

### Technical Setup:
- [ ] MySQL is running and accessible
- [ ] Database has all data loaded (830 matches, 2.6M events)
- [ ] Your 2-3 SQL queries are saved and tested
- [ ] You can access the database quickly during demo

### Materials Ready:
- [ ] ER diagram (printed or on slide)
- [ ] Fact Constellation diagram
- [ ] Presentation slides (4-5 slides)
- [ ] SQL query results (screenshots or live demo)
- [ ] Table row counts handy (can show `SHOW TABLES; SELECT COUNT(*) FROM...`)

### Knowledge Check:
- [ ] Can explain Fact Constellation in 1 minute
- [ ] Can name all 23 tables by category
- [ ] Can explain why MySQL was chosen
- [ ] Can describe sentinel record strategy
- [ ] Can explain your contribution clearly

### Coordination:
- [ ] Know when you speak (which sections)
- [ ] Know how to transition to next speaker
- [ ] Have backup plan if technology fails
- [ ] Team has practiced full demo at least once

---

## 🎉 Summary

### Your Role in Demonstration:

**YOU ARE RESPONSIBLE FOR:**
1. ✅ Explaining the conceptual schema (Fact Constellation) - **3-4 minutes**
2. ✅ Explaining destination tables you designed - **1 minute**
3. ✅ Showing ER diagram and relationships - **1 minute**
4. ✅ Contributing 2-3 business queries showing schema design - **2-3 minutes**
5. ✅ Describing your contribution - **1 minute**

**TOTAL SPEAKING TIME:** 8-10 minutes (out of 20-25 total)

### "15 Business Queries" Meaning:

**Answer:** Can be shown as:
- SQL queries with results (most common)
- Power BI visualizations (visual analytics)
- Mix of both (recommended)

**Your part:** Contribute 2-3 queries that showcase your schema design quality

### Guide Alignment:

**Answer:** Your guide (MEMBER2_BEGINNERS_GUIDE.md) covers 95% of what you need. You just need to:
1. Create your 2-3 specific SQL queries
2. Make visual diagrams/slides
3. Practice speaking your parts

---

**You're ready!** Your guide gives you all the knowledge. Now just prepare the visuals, queries, and practice! 💪🚀

---

**Document Created:** November 2, 2025  
**For:** Team Member 2 - Database Schema Designer  
**Purpose:** Map university demonstration requirements to your role
