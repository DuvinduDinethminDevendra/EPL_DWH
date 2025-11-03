# Mermaid Diagrams for Presentation
## Copy these into VS Code and preview to export as images

---

## Diagram 1: Complete Schema Architecture

```mermaid
graph TB
    subgraph Sources["📁 DATA SOURCES"]
        JSON["StatsBomb JSON<br/>380 files<br/>1.3M+ events"]
        CSV["CSV Files<br/>E0 Season<br/>830 matches"]
        API["API Calls<br/>football-data.org<br/>Teams/Players"]
        XLS["Excel Files<br/>Stadiums<br/>Referees"]
    end
    
    subgraph Staging["🏗️ STAGING LAYER (6 tables)"]
        STG1["stg_events_raw"]
        STG2["stg_e0_match_raw"]
        STG3["stg_team_raw"]
        STG4["stg_player_raw"]
        STG5["stg_referee_raw"]
        STG6["stg_player_stats_fbref"]
    end
    
    subgraph Dims["🗂️ DIMENSIONS (6 tables)"]
        DIM1["dim_date<br/>17,520 rows"]
        DIM2["dim_team<br/>25 rows"]
        DIM3["dim_player<br/>6,847 rows"]
        DIM4["dim_referee<br/>32 rows"]
        DIM5["dim_stadium<br/>25 rows"]
        DIM6["dim_season<br/>7 rows"]
    end
    
    subgraph Facts["📊 FACT TABLES (3)"]
        F1["fact_match<br/>830 rows<br/>Match Level"]
        F2["fact_match_events<br/>1.3M+ rows<br/>Event Level"]
        F3["fact_player_stats<br/>1.6K rows<br/>Player Level"]
    end
    
    subgraph Audit["📝 AUDIT LAYER (6)"]
        AUD1["ETL_Log"]
        AUD2["ETL_File_Manifest"]
        AUD3["ETL_Api_Manifest"]
        AUD4["ETL_Excel_Manifest"]
        AUD5["ETL_Events_Manifest"]
        AUD6["ETL_JSON_Manifest"]
    end
    
    JSON --> STG1
    CSV --> STG2
    API --> STG3
    API --> STG4
    XLS --> STG5
    XLS --> STG6
    
    STG1 --> DIM1
    STG2 --> DIM1
    STG2 --> DIM2
    STG3 --> DIM2
    STG4 --> DIM3
    STG5 --> DIM4
    STG5 --> DIM5
    STG6 --> DIM6
    
    DIM1 -.FK.-> F1
    DIM2 -.FK.-> F1
    DIM3 -.FK.-> F1
    DIM4 -.FK.-> F1
    DIM5 -.FK.-> F1
    DIM6 -.FK.-> F1
    
    F1 -.FK.-> F2
    DIM3 -.FK.-> F2
    DIM2 -.FK.-> F2
    
    DIM3 -.FK.-> F3
    DIM2 -.FK.-> F3
    DIM6 -.FK.-> F3
    
    STG1 --> AUD6
    STG2 --> AUD2
    STG3 --> AUD3
    STG4 --> AUD3
    STG5 --> AUD4
    STG6 --> AUD4

    style Sources fill:#e1f5ff
    style Staging fill:#fff3e0
    style Dims fill:#f3e5f5
    style Facts fill:#e8f5e9
    style Audit fill:#fce4ec
```

---

## Diagram 2: Fact Constellation Pattern

```mermaid
graph TD
    subgraph Conformed["🌟 CONFORMED DIMENSIONS"]
        D1[dim_date]
        D2[dim_team]
        D3[dim_player]
        D4[dim_referee]
        D5[dim_stadium]
        D6[dim_season]
    end
    
    subgraph Facts["📊 FACT CONSTELLATION"]
        F1["fact_match<br/>Summary Level<br/>830 rows<br/><br/>6 FK to dimensions"]
        F2["fact_match_events<br/>Detail Level<br/>1.3M+ rows<br/><br/>3 FK to dimensions<br/>1 FK to fact_match"]
        F3["fact_player_stats<br/>Player Level<br/>1.6K rows<br/><br/>3 FK to dimensions"]
    end
    
    D1 -.->|FK| F1
    D2 -.->|FK| F1
    D3 -.->|FK| F1
    D4 -.->|FK| F1
    D5 -.->|FK| F1
    D6 -.->|FK| F1
    
    F1 -.->|FK| F2
    D2 -.->|FK| F2
    D3 -.->|FK| F2
    
    D2 -.->|FK| F3
    D3 -.->|FK| F3
    D6 -.->|FK| F3
    
    style D1 fill:#9fa8da
    style D2 fill:#9fa8da
    style D3 fill:#9fa8da
    style D4 fill:#9fa8da
    style D5 fill:#9fa8da
    style D6 fill:#9fa8da
    style F1 fill:#aed581
    style F2 fill:#ffb74d
    style F3 fill:#81c784
```

---

## Diagram 3: Foreign Key Relationships (Detailed)

```mermaid
erDiagram
    dim_date ||--o{ fact_match : "date_id (FK)"
    dim_team ||--o{ fact_match : "home_team_id (FK)"
    dim_team ||--o{ fact_match : "away_team_id (FK)"
    dim_referee ||--o{ fact_match : "referee_id (FK)"
    dim_stadium ||--o{ fact_match : "stadium_id (FK)"
    dim_season ||--o{ fact_match : "season_id (FK)"
    
    fact_match ||--o{ fact_match_events : "match_id (FK)"
    dim_player ||--o{ fact_match_events : "player_id (FK)"
    dim_team ||--o{ fact_match_events : "team_id (FK)"
    
    dim_player ||--o{ fact_player_stats : "player_id (FK)"
    dim_team ||--o{ fact_player_stats : "team_id (FK)"
    dim_season ||--o{ fact_player_stats : "season_id (FK)"
    
    dim_date {
        int date_id PK
        date full_date
        int day
        int month
        int year
    }
    
    dim_team {
        int team_id PK
        string team_name
        string team_code
        string founded
    }
    
    dim_player {
        int player_id PK
        string player_name
        string position
        string nationality
    }
    
    fact_match {
        int match_id PK
        int date_id FK
        int season_id FK
        int home_team_id FK
        int away_team_id FK
        int referee_id FK
        int stadium_id FK
        int home_goals
        int away_goals
    }
    
    fact_match_events {
        int event_id PK
        int match_id FK
        int player_id FK
        int team_id FK
        string event_type
        int minute
    }
    
    fact_player_stats {
        int stat_id PK
        int player_id FK
        int team_id FK
        int season_id FK
        int goals
        int assists
    }
```

---

## Diagram 4: ETL Data Flow

```mermaid
flowchart LR
    subgraph Extract["1️⃣ EXTRACT"]
        SRC1[StatsBomb API]
        SRC2[CSV Files]
        SRC3[Football-Data API]
        SRC4[Excel Files]
    end
    
    subgraph Stage["2️⃣ STAGING"]
        ST1[Raw Tables<br/>6 staging tables]
        ST2[Validation]
        ST3[Deduplication]
    end
    
    subgraph Transform["3️⃣ TRANSFORM"]
        TR1[Clean Data]
        TR2[Standardize]
        TR3[Enrich]
    end
    
    subgraph Load["4️⃣ LOAD"]
        L1[Dimensions<br/>6 tables]
        L2[Facts<br/>3 tables]
        L3[Audit<br/>6 tables]
    end
    
    SRC1 --> ST1
    SRC2 --> ST1
    SRC3 --> ST1
    SRC4 --> ST1
    
    ST1 --> ST2
    ST2 --> ST3
    ST3 --> TR1
    
    TR1 --> TR2
    TR2 --> TR3
    
    TR3 --> L1
    L1 --> L2
    
    ST1 -.log.-> L3
    TR1 -.log.-> L3
    L1 -.log.-> L3
    L2 -.log.-> L3
    
    style Extract fill:#e3f2fd
    style Stage fill:#fff9c4
    style Transform fill:#f3e5f5
    style Load fill:#c8e6c9
```

---

## Diagram 5: Table Categories Pie Chart (Concept)

```mermaid
pie title EPL Data Warehouse - 23 Tables Distribution
    "Dimensions (6)" : 26
    "Facts (3)" : 13
    "Staging (6)" : 26
    "Audit (6)" : 26
    "Mappings (2)" : 9
```

---

## Diagram 6: Query Flow Example

```mermaid
sequenceDiagram
    participant User
    participant BI as Power BI
    participant F1 as fact_match
    participant F2 as fact_match_events
    participant D1 as dim_team
    participant D2 as dim_player
    
    User->>BI: "Show Liverpool goals in 2023-24"
    BI->>F1: JOIN ON season, team
    F1->>D1: FK: home_team_id = 'Liverpool'
    F1->>F2: FK: match_id
    F2->>D2: FK: player_id
    D2->>BI: player_name, goals
    BI->>User: Liverpool scored 86 goals
```

---

## How to Use These Diagrams

### Step 1: Preview in VS Code
1. Install extension: "Markdown Preview Mermaid Support"
2. Open this file
3. Click "Preview" button (Ctrl+Shift+V)
4. Mermaid diagrams will render as visuals

### Step 2: Export as Images
1. Right-click on rendered diagram
2. Select "Copy Image" or "Save Image As"
3. Save as PNG/SVG
4. Insert into PowerPoint

### Step 3: Edit Online (Alternative)
1. Visit: https://mermaid.live
2. Copy-paste diagram code
3. Edit colors/layout
4. Download as PNG/SVG

---

## Recommended Diagrams for Your 5-Minute Presentation

| Slide | Use This Diagram | Why |
|-------|------------------|-----|
| 2 - Overview | Diagram 5 (Pie Chart) | Shows 23 tables distribution |
| 3 - Constellation | Diagram 2 (Fact Constellation) | Clear pattern visualization |
| 4 - Data Flow | Diagram 1 or 4 (ETL Flow) | Shows source → destination |
| 5 - FKs | Diagram 3 (ER Diagram) | Shows relationships |

---

## Color Palette Used

- **Data Sources**: Light Blue (#e1f5ff)
- **Staging**: Light Orange (#fff3e0)
- **Dimensions**: Light Purple (#f3e5f5)
- **Facts**: Light Green (#e8f5e9)
- **Audit**: Light Pink (#fce4ec)

Feel free to adjust colors in PowerPoint for your university's theme!

---

## Tips for Best Results

1. **Export High Resolution**: Use SVG format if PowerPoint supports it
2. **Maintain Aspect Ratio**: Don't stretch diagrams
3. **Add Labels**: Add text boxes to highlight key areas
4. **Animate**: Use PowerPoint animations to reveal parts step-by-step
5. **Practice Pointing**: Know which arrows to point at during presentation

---

**Next Steps:**
1. Preview these diagrams in VS Code
2. Export the 4 key diagrams
3. Insert into your PowerPoint slides
4. Add your text content from PRESENTATION_5MIN_GUIDE.md
5. Practice presenting!

Good luck! 🎨
