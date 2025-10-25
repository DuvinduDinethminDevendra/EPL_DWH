# EPL Data Warehouse Business Overview

## 1. Introduction - Name of the Business
**Business Name:** EPL Data Warehouse (EPL_DWH)

A comprehensive data warehouse solution for the English Premier League, designed to support analytics, reporting, and business intelligence for football data.

---

## 2. Facilities
- Dockerized MySQL 8.0 database for scalable, reliable storage
- Python-based ETL pipeline for automated data integration
- Staging, audit, and manifest tables for data quality and traceability
- Modular folder structure for raw, staging, and processed data
- Support for local and cloud deployment

---

## 3. Tools and Technologies
- **Database:** MySQL 8.0 (Docker)
- **ETL:** Python 3.13, pandas, SQLAlchemy
- **Data Integration:** openpyxl (Excel), REST API, CSV, JSON
- **Orchestration:** Docker Compose
- **Version Control:** Git
- **Documentation:** Markdown, ERD diagrams

---

## 4. Data Sources
- **JSON:** Player data from fbref.com
- **API:** Team data from football-data.org
- **CSV:** Match results (E0Season_*.csv)
- **Excel:** Referee and stadium data
- **Audit:** Manifest tables for all sources

---

## 5. Logical Schema
- **Dimensions:**
  - Player (dim_player)
  - Team (dim_team)
  - Referee (dim_referee)
  - Stadium (dim_stadium)
  - Date (dim_date)
  - Season (dim_season)
- **Facts:**
  - Match (fact_match)
  - Player Stats (fact_player_stats)
  - Match Events (fact_match_events)
- **Audit/Control:**
  - ETL_Log, ETL_File_Manifest, ETL_Api_Manifest, ETL_Excel_Manifest, ETL_JSON_Manifest

---

## 6. Physical Schema
- **Database:** epl_dw
- **Tables:**
  - Staging: stg_player_raw, stg_team_raw, stg_e0_match_raw, stg_referee_raw, stg_player_stats_fbref
  - Dimensions: dim_player, dim_team, dim_referee, dim_stadium, dim_date, dim_season
  - Facts: fact_match, fact_player_stats, fact_match_events
  - Audit: ETL_Log, ETL_File_Manifest, ETL_Api_Manifest, ETL_Excel_Manifest, ETL_JSON_Manifest
- **Indexes:**
  - Primary keys and foreign keys for referential integrity
  - Unique constraints on business keys

---

## 7. Data Warehouse Design Steps
1. **Requirement Analysis:** Identify business needs and analytics goals
2. **Source Data Mapping:** Catalog all raw data sources (JSON, API, CSV, Excel)
3. **Staging Layer:** Load raw data into staging tables for cleaning and validation
4. **Data Cleaning & Conformance:** Normalize names, handle missing values, conform to dimension standards
5. **Dimension Table Design:** Create slowly changing dimensions with surrogate keys and sentinel rows
6. **Fact Table Design:** Model fact tables with business keys and foreign key joins
7. **ETL Pipeline Development:** Build automated extract, transform, and load scripts in Python
8. **Audit & Manifest Tracking:** Implement manifest tables for data lineage and quality
9. **Testing & Validation:** Run full ETL cycles, validate joins and data completeness
10. **Deployment:** Dockerize for local/cloud deployment, document usage and maintenance

---

**For more details, see the main README.md and schema files in the repository.**
