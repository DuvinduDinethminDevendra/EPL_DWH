
# EPL Data Warehouse Project

This project implements an ETL (Extract, Transform, Load) pipeline to build a Star Schema Data Warehouse for English Premier League (EPL) match and player statistics. The database is hosted in a dedicated MySQL Docker container to ensure a consistent environment across development machines.

## Prerequisites

To run this project, you must have the following software installed on your system:

  * **Docker Desktop:** (Includes Docker Engine and Docker Compose)
  * **Python 3.9+**
  * **Git**

## Setup Guide

Follow these steps to get the environment running on your local machine.

### 1\. Clone the Repository

```bash
git clone https://github.com/DuvinduDinethminDevendra/EPL_DWH
cd EPL_DWH
```

### 2\. Configure the Database (Docker)

This project uses Docker Compose to manage the MySQL database container.

**Create the `docker-compose.yml` file** (if you don't have one yet) and define your MySQL service.


```yaml
version: "3.8" # OK, but can be removed for modern Compose V2
services:
  db:
    image: mysql:8.0
    container_name: epl_mysql
    restart: unless-stopped
    environment:
     
      MYSQL_ROOT_PASSWORD: 1234 #password
      MYSQL_DATABASE: epl_dw
    ports:
      
      - "3307:3306" 
    volumes:
      - ./mysql_data:/var/lib/mysql
      - ./src/sql:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  adminer:
    image: adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    
    depends_on:
      - db
```

**Start the Container:**

Run the following command in the project root directory. This will download the MySQL image, create the `epl_dw` database, and execute the `create_schema.sql` script to build your tables.

```bash
docker-compose up -d
```
OR IF NEED TO CREATE A LOCAL INSTANCE AS WELL
```bash
mysql -u root -p1234 < "src\sql\create_schema.sql"
```

### 3\. Setup Python Environment

This project uses a virtual environment (`.venv`) for dependency management.

**A. Create and Activate the Virtual Environment**

On Windows (PowerShell):

```powershell
# Create the environment
py -m venv .venv

# Activate the environment (Required for every new terminal session)
. .venv/Scripts/Activate.ps1
```
If you wont to run the v env in comman promt
```command prompt
.venv\Scripts\activate.bat
```

*(Your prompt should now start with `(.venv)`)*

**B. Install Python Dependencies**

Ensure you have a `requirements.txt` file listing packages like `sqlalchemy` and `mysql-connector-python`.

```bash
# Example contents of requirements.txt:
# sqlalchemy
# mysql-connector-python
# pandas

pip install -r requirements.txt
```

### 4\. Run the ETL Pipeline

Once the database container is running and the Python environment is active, you can run the ETL pipeline.

**Complete ETL Pipeline (Recommended):**
```bash
python -m src.etl.main --full-etl
```

**Run Only Staging Load:**
```bash
python -m src.etl.main --staging
```

**Run Only Warehouse Load:**
```bash
python -m src.etl.main --warehouse
```

**Test Database Connectivity:**
```bash
python -m src.etl.main --test-db
```

## ETL Pipeline Overview

The project implements a complete ETL pipeline with three main stages:

### **Stage 1: Staging (Extract & Load)**
Loads raw data from multiple sources into staging tables:

| Source | Format | Target Table | Records |
|--------|--------|--------------|---------|
| **JSON Files** | JSON | `stg_player_raw` | ~6,834 players |
| **API (football-data.org)** | REST API | `stg_team_raw` | ~60 teams |
| **CSV Files** | CSV | `stg_e0_match_raw` | ~830 matches |
| **Excel Files** | XLSX | `stg_referee_raw`, `dim_stadium` | ~32 referees, ~32 stadiums |

**Key Features:**
- ✅ Idempotent processing (skips already-loaded files)
- ✅ Comprehensive audit trail via manifest tables
- ✅ Error logging and recovery
- ✅ Smart Excel sheet detection (finds appropriate sheets by name)

### **Stage 2: Transform & Load (Dimensions)**
Cleans and transforms staging data into dimension tables:

| Dimension | Records | Key Attributes |
|-----------|---------|-----------------|
| `dim_date` | 17,803 | Calendar 1992-2040 with week numbers |
| `dim_team` | 25 | Team name, code, city |
| `dim_player` | 6,834 | Player name, position, nationality |
| `dim_referee` | 32 | Name, DOB, nationality, PL debut, status |
| `dim_stadium` | 32 | Name, capacity, city, club, coordinates |
| `dim_season` | 6 | Season name, start/end dates |

**Cleaning Logic:**
- Standardizes team names (handles "Man City" → "Manchester City" mappings)
- Removes duplicates and null values
- Creates surrogate keys and business keys

### **Stage 3: Load (Facts)**
Loads fact tables with foreign key references to dimensions:

| Fact Table | Records | Measures |
|-----------|---------|----------|
| `fact_match` | 830 | Goals, shots, fouls, cards, results |
| `fact_match_events` | - | Event type, player, minute (ready) |
| `fact_player_stats` | - | Minutes, goals, assists, cards (ready) |

## Data Sources

### Excel Files
Place Excel files in `data/raw/xlsx/` folder. The system automatically detects:
- **Referee files** (containing "referee" in filename) → loads to `stg_referee_raw`
- **Stadium files** (containing "stadium" in filename) → loads to `dim_stadium`

**Expected Column Names:**
- **Referees:** `Referee_Name`, `Date_of_Birth`, `Nationality`, `Premier_League_Debut`, `Status`, `Notes`
- **Stadiums:** `Stadium_Name`, `Capacity`, `City`, `Club`, `Opened`, `Coordinates`, `Notes`

### API Integration
- **football-data.org API** - Fetches current team data for seasons 2023-2025
- Stores full API responses including squads and staff details

### CSV Files
- **E0 Series (fbref)** - Match results from football-reference.com
- Supports multiple seasons and divisions

### JSON Files
- **Squad data** - Player information from football-data.org
- Nested player and staff information

## Data Warehouse Schema

### Key Design Patterns

**1. Date Dimension (Type 1 - Slowly Changing)**
- Pre-populated calendar from 1992 to 2040
- Supports week-based analysis
- Extensible for match day flags

**2. Team Conformation**
- Uses CASE statement CTE to map raw team names to canonical forms
- Handles abbreviations and historical naming variations

**3. Surrogate Keys**
- Sentinel rows (-1) for unknown/missing dimensions
- Ensures referential integrity with NOT NULL constraints

**4. Audit Trail**
- `ETL_Log` - Records all ETL job execution details
- `ETL_File_Manifest` - Tracks CSV file loads
- `ETL_Api_Manifest` - Tracks API calls
- `ETL_Excel_Manifest` - Tracks Excel file loads
- `ETL_JSON_Manifest` - Tracks JSON file loads

## Architecture

```
┌─────────────────────────────────────────────────┐
│         DATA EXTRACTION LAYER                   │
├─────────────────────────────────────────────────┤
│ JSON Reader │ API Client │ CSV Reader │ Excel   │
│             │            │           │ Reader  │
└──────────────┬───────────┬───────────┬──────────┘
               │           │           │
┌──────────────▼───────────▼───────────▼──────────┐
│        STAGING TABLES (Raw Data)                │
├──────────────────────────────────────────────────┤
│ stg_player_raw │ stg_team_raw │ stg_e0_match... │
│ stg_referee_raw │ stg_player_stats_fbref      │
└─────────────┬──────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────┐
│        TRANSFORM & CLEAN LAYER                 │
├──────────────────────────────────────────────────┤
│ Deduplication │ Standardization │ Conformation │
└────────────┬─────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────┐
│    DIMENSION TABLES (Conformed Data)          │
├──────────────────────────────────────────────────┤
│ dim_date │ dim_team │ dim_player │ dim_referee │
│ dim_stadium │ dim_season                       │
└────────────┬─────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────┐
│      FACT TABLES (Analysis Ready)             │
├──────────────────────────────────────────────────┤
│ fact_match │ fact_match_events │ fact_player...│
└──────────────────────────────────────────────────┘
```

## Database Connection Details

These details are used by the Python application to connect to the Docker container.

| Setting | Environment Variable | Default Value | Docker Service Name |
| :--- | :--- | :--- | :--- |
| **Host** | `MYSQL_HOST` | `localhost` | `epl_mysql` |
| **Port** | `MYSQL_PORT` | `3307` | N/A (Host Port) |
| **User** | `MYSQL_USER` | `root` | `root` |
| **Password** | `MYSQL_PASSWORD` | `1234` | `1234` |
| **Database** | `MYSQL_DB` | `epl_dw` | `epl_dw` |

## Viewing the Database

You can connect to the running `epl_mysql` container using any standard database client (e.g., DBeaver, MySQL Workbench, TablePlus) with the connection details provided above.

**Host:** `localhost`
**Port:** `3307`
**User:** `root`
**Password:** `1234`

## Cleanup

To stop and remove the Docker container and its data (if you didn't use a volume, otherwise it just stops the service):

```bash
docker-compose down
```

To deactivate the virtual environment:

```bash
deactivate
```
