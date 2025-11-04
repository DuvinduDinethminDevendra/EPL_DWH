# ⚽ EPL Data Warehouse

> A comprehensive data warehouse solution for English Premier League match data, integrating multiple sources into a unified analytical platform.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MySQL 8.0](https://img.shields.io/badge/mysql-8.0-orange.svg)](https://www.mysql.com/)

---

## 📋 Overview

The EPL Data Warehouse is an end-to-end ETL (Extract, Transform, Load) pipeline that collects, processes, and organizes English Premier League football data from multiple sources into a structured data warehouse. The project implements a **Fact Constellation schema** (also known as Galaxy Schema) with 23 tables handling over **2.7 million records**, enabling comprehensive analysis of matches, player performances, and match events.

### 🎯 Project Purpose

This data warehouse serves as:
- **Educational Resource**: A complete example of dimensional modeling and ETL pipeline development
- **Analytics Platform**: Ready-to-use database for EPL match analysis and visualization
- **Integration Showcase**: Demonstrates combining multiple data sources (APIs, JSON, CSV, Excel) into a unified schema

---

## ✨ Key Features

- **📊 Multiple Data Sources**: Integrates 4 different data source types
- **🏗️ Fact Constellation Schema**: 6 dimensions, 3 fact tables for flexible multi-perspective analysis
- **🔒 Data Integrity**: 15+ foreign key constraints ensuring referential integrity
- **📈 Large Scale**: Handles 2.7M+ records with optimized loading strategies
- **🔄 Idempotent Pipeline**: Manifest tracking prevents duplicate data loads
- **⚡ Fast Testing**: Optional data limiting for quick pipeline validation
- **🎨 Ready for BI**: Structured for Power BI, Tableau, or other visualization tools

---

## 📊 Data Sources

The warehouse integrates data from **4 different sources**:

| Source | Type | Records | Content |
|--------|------|---------|---------|
| **StatsBomb Open Data** | JSON (380 files) | 2.6M+ events | Detailed match events, player actions, ball movements |
| **CSV Match Data** | CSV | 830 matches | Match results, scores, dates, venues |
| **Football-Data.org API** | REST API | 25 teams, 6.8K players | Team information, player rosters |
| **Excel Files** | XLSX | 32 referees, 25 stadiums | Stadium details, referee information |

### 📥 What Data is Collected?

- **Match Events**: Every pass, shot, tackle, foul, and substitution (2.6M+ events)
- **Match Results**: Scores, dates, teams, referees, stadiums (830 matches)
- **Team Information**: EPL teams, codes, founded dates (25 teams)
- **Player Details**: Names, positions, nationalities (6,847 players)
- **Referees & Stadiums**: Venue and official information (32 referees, 25 stadiums)
- **Temporal Data**: Date dimensions covering multiple seasons (17,500+ dates)

---

## 🏗️ Database Architecture

### Schema Design: Fact Constellation Pattern

The warehouse uses a **Fact Constellation** (Galaxy Schema) design with multiple fact tables sharing common dimensions:

```
📊 23 Tables Total:
├── 🗂️  6 Dimensions (Reference Data)
│   ├── dim_date (17,500 rows) - Calendar dates
│   ├── dim_team (25 rows) - EPL teams
│   ├── dim_player (6,847 rows) - Players
│   ├── dim_referee (32 rows) - Match officials
│   ├── dim_stadium (25 rows) - Venues
│   └── dim_season (7 rows) - Seasons
│
├── 📈 3 Fact Tables (Transaction Data)
│   ├── fact_match (830 rows) - Match summaries
│   ├── fact_match_events (2.6M+ rows) - Event details
│   └── fact_player_stats (1.6K rows) - Player performance
│
├── 🔗 2 Mapping Tables (ID Translation)
│   ├── dim_team_mapping - Bridge different team IDs
│   └── dim_match_mapping - Link StatsBomb to CSV matches
│
├── 📝 6 Audit Tables (ETL Tracking)
│   └── ETL manifests for deduplication
│
└── 🏗️  6 Staging Tables (Temporary Storage)
    └── Raw data buffer before transformation
```

### Why Fact Constellation?

- **Multiple Perspectives**: Analyze data at match level, event level, or player level
- **Shared Dimensions**: Consistent reference data across all facts
- **Flexible Queries**: Drill down from match → event → player seamlessly
- **Scalable Design**: Easy to add new fact tables without changing dimensions

---

## 🚀 Quick Start

### Prerequisites

- **MySQL 8.0** (via Docker or local installation)
- **Python 3.9+**
- **Git**
- **500MB free disk space** (for StatsBomb data)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DuvinduDinethminDevendra/EPL_DWH.git
   cd EPL_DWH
   ```

2. **Start MySQL database**
   ```bash
   # Using Docker
   docker-compose up -d
   
   # Verify database is running
   docker ps | grep epl_mysql
   ```

3. **Set up Python environment**
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Run the ETL pipeline**
   ```bash
   # Full pipeline (all data, ~10 minutes)
   python -m src.etl.main --full-etl-and-facts
   
   # Quick test (first 10 files, ~40 seconds)
   python -m src.etl.main --full-etl-and-facts --limit-data 10
   ```

### Verify Installation

```sql
-- Check loaded data
USE epl_warehouse;

SELECT 'Matches' as table_name, COUNT(*) as rows FROM fact_match
UNION ALL
SELECT 'Events', COUNT(*) FROM fact_match_events
UNION ALL
SELECT 'Players', COUNT(*) FROM dim_player
UNION ALL
SELECT 'Teams', COUNT(*) FROM dim_team;
```

Expected results:
- Matches: 830 rows
- Events: 2,675,770 rows
- Players: 6,847 rows
- Teams: 25 rows

---

## 💻 Usage

### ETL Pipeline Commands

```bash
# Recommended: Full pipeline with all data
python -m src.etl.main --full-etl-and-facts

# Quick testing with limited data
python -m src.etl.main --full-etl-and-facts --limit-data 50

# Test database connection
python -m src.etl.main --test-db

# Show all available commands
python -m src.etl.main --help
```

### Example Queries

```sql
-- Top scorers by team
SELECT 
    t.team_name,
    p.player_name,
    ps.goals,
    ps.assists
FROM fact_player_stats ps
JOIN dim_player p ON ps.player_id = p.player_id
JOIN dim_team t ON ps.team_id = t.team_id
ORDER BY ps.goals DESC
LIMIT 10;

-- Match events breakdown
SELECT 
    event_type,
    COUNT(*) as event_count
FROM fact_match_events
GROUP BY event_type
ORDER BY event_count DESC;

-- Home vs Away performance
SELECT 
    home.team_name as home_team,
    away.team_name as away_team,
    m.home_goals,
    m.away_goals,
    d.full_date as match_date
FROM fact_match m
JOIN dim_team home ON m.home_team_id = home.team_id
JOIN dim_team away ON m.away_team_id = away.team_id
JOIN dim_date d ON m.date_id = d.date_id
ORDER BY d.full_date DESC
LIMIT 10;
```

---

## 📚 Documentation

Detailed documentation is available in the repository:

- **[ETL_PIPELINE_GUIDE.md](ETL_PIPELINE_GUIDE.md)** - Complete ETL process explanation
- **[DATABASE_RELATIONSHIPS_ER_DIAGRAM.md](DATABASE_RELATIONSHIPS_ER_DIAGRAM.md)** - Database schema and relationships
- **[FACT_CONSTELLATION_CONFIRMATION.md](FACT_CONSTELLATION_CONFIRMATION.md)** - Schema pattern documentation
- **[TEAM_DIVISION_COMPREHENSIVE.md](TEAM_DIVISION_COMPREHENSIVE.md)** - Project team structure and roles

---

## 🛠️ Built With

- **Database**: MySQL 8.0
- **Language**: Python 3.9+
- **ETL Framework**: Custom Python pipeline
- **Key Libraries**: 
  - `pandas` - Data manipulation
  - `SQLAlchemy` - Database ORM
  - `requests` - API calls
  - `openpyxl` - Excel file processing

---

## 📈 Data Statistics

| Metric | Value |
|--------|-------|
| **Total Records** | 2,700,000+ |
| **Matches Covered** | 830 EPL matches |
| **Match Events** | 2,675,770 detailed events |
| **Players Tracked** | 6,847 unique players |
| **Teams** | 25 EPL teams |
| **Time Coverage** | 2023-2025 seasons |
| **Data Sources** | 4 different types |
| **Processing Time** | ~10 minutes (full pipeline) |

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

**Data Sources Licenses:**
- StatsBomb Open Data: [Creative Commons Attribution 4.0](https://github.com/statsbomb/open-data)
- CSV Match Data: Public domain
- Football-Data.org: [API Terms of Use](https://www.football-data.org/documentation/api)

---

## 🤝 Contributing

This is an educational project completed as part of a university data warehouse course. While the project is complete, feedback and suggestions are welcome!

---

## 👥 Team

This project was developed by a team of 5 students as part of the ICT 3233 Data Warehousing course:

- **https://github.com/DilmiDevindi**: ETL Pipeline Development 
- **https://github.com/lakipop**: Database Schema Design
- **https://github.com/SahanVkaru**: Dimension Table Implementation
- **https://github.com/DuvinduDinethminDevendra**: Fact Table Implementation
- **https://github.com/HiruniKapuge**: Business Intelligence & Visualization

---

## 🙏 Acknowledgments

- **StatsBomb** for providing open football event data
- **Football-Data.org** for team and player information API
- Course instructors and mentors for guidance throughout the project

---

## 📧 Contact

**Project Repository**: [github.com/DuvinduDinethminDevendra/EPL_DWH](https://github.com/DuvinduDinethminDevendra/EPL_DWH)

For questions or feedback, please open an issue on GitHub.

---

**⭐ If you find this project useful, please consider giving it a star!**
