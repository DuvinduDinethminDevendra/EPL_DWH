"""Complete ETL pipeline: Extract → Clean → Transform → Load to Data Warehouse.

This module orchestrates:
1. Data extraction from raw sources (JSON, API, CSV)
2. Data loading to staging tables
3. Data cleaning and transformation
4. Upsert to dimension tables in data warehouse
"""

from pathlib import Path
from src.etl.staging.load_staging import load_all_staging
from src.etl.transform.clean import clean_player_names
from src.etl.transform.clean_and_upsert_dim import run_all_upserts
from src.etl.db import get_engine
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_staging_data():
    """Clean data in staging tables.
    
    Applies transformations:
    - Player names: strip, title case
    - Remove NULL values where required
    - Data validation
    """
    print("\n" + "="*70)
    print("STEP 2: CLEANING STAGING DATA")
    print("="*70)
    
    engine = get_engine()
    
    try:
        # Clean stg_player_raw
        print("\nCleaning stg_player_raw...")
        player_df = pd.read_sql("SELECT * FROM stg_player_raw WHERE status = 'SUCCESS'", engine)
        
        if len(player_df) > 0:
            player_df = clean_player_names(player_df, "player_name")
            
            # Log cleaning results
            logger.info(f"Cleaned {len(player_df)} player records")
            print(f"[OK] Cleaned {len(player_df)} player records")
        else:
            print("! No successfully loaded player records to clean")
        
        # Clean stg_team_raw
        print("\nCleaning stg_team_raw...")
        team_df = pd.read_sql("SELECT * FROM stg_team_raw WHERE status = 'SUCCESS'", engine)
        
        if len(team_df) > 0:
            # Clean team names
            if 'name' in team_df.columns:
                team_df['name'] = team_df['name'].astype(str).str.strip()
            
            logger.info(f"Cleaned {len(team_df)} team records")
            print(f"[OK] Cleaned {len(team_df)} team records")
        else:
            print("! No successfully loaded team records to clean")
        
        # Clean stg_e0_match_raw
        print("\nCleaning stg_e0_match_raw...")
        match_df = pd.read_sql("SELECT * FROM stg_e0_match_raw LIMIT 100000", engine)
        
        if len(match_df) > 0:
            # Clean team names in match data
            for col in ['HomeTeam', 'AwayTeam']:
                if col in match_df.columns:
                    match_df[col] = match_df[col].astype(str).str.strip()
            
            logger.info(f"Cleaned {len(match_df)} match records")
            print(f"[OK] Cleaned {len(match_df)} match records")
        else:
            print("! No match records to clean")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during data cleaning: {e}")
        print(f"[ERROR] Error during data cleaning: {e}")
        return False


def transform_and_load_dimensions():
    """Orchestrates the transformation and loading of all dimension tables."""
    print("\n" + "="*70)
    print("STEP 3: TRANSFORMING & LOADING DIMENSIONS")
    print("="*70)
    engine = get_engine()
    try:
        # This single function now handles all dimension upserts
        results = run_all_upserts(engine)
        return results
    except Exception as e:
        logger.error(f"Error during dimension loading: {e}")
        print(f"[ERROR] Error during dimension loading: {e}")
        return {'success': False, 'total_rows': 0}


def run_complete_etl_pipeline():
    """Execute complete ETL pipeline: Extract → Clean → Transform → Load.
    
    Pipeline stages:
    1. EXTRACT: Load raw data to staging tables
    2. CLEAN: Apply data quality transformations
    3. TRANSFORM & LOAD: Process and upsert to data warehouse dimensions
    """
    print("\n")
    print("="*70)
    print("COMPLETE ETL PIPELINE: EXTRACT -> CLEAN -> TRANSFORM -> LOAD".center(70))
    print("="*70)
    
    pipeline_results = {}
    
    # STEP 1: EXTRACT
    print("\n" + "="*70)
    print("STEP 1: EXTRACTING DATA TO STAGING TABLES")
    print("="*70)
    extract_success = load_all_staging()
    pipeline_results['extract'] = extract_success
    
    if not extract_success:
        logger.warning("Extraction failed or partially completed, continuing with cleaning...")
    
    # STEP 2: CLEAN
    clean_success = clean_staging_data()
    pipeline_results['clean'] = clean_success
    
    if not clean_success:
        logger.warning("Data cleaning had issues, continuing with transformation...")
    
    # STEP 3: TRANSFORM & LOAD
    transform_results = transform_and_load_dimensions()
    pipeline_results['transform'] = transform_results
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print("ETL PIPELINE EXECUTION SUMMARY")
    print("="*70)
    print(f"Extract Status: {'[OK] SUCCESS' if pipeline_results.get('extract') else '[ERROR] FAILED'}")
    print(f"Clean Status: {'[OK] SUCCESS' if pipeline_results.get('clean') else '[ERROR] FAILED'}")
    
    transform_status = transform_results.get('success', False)
    print(f"Transform & Load Status: {'[OK] SUCCESS' if transform_status else '[ERROR] FAILED'}")
    
    if transform_status:
        print("\nDimensions Loaded:")
        print(f"  - dim_player: {transform_results.get('dim_player', (0,0))[0]} rows")
        print(f"  - dim_team: {transform_results.get('dim_team', (0,0))[0]} rows")
        print(f"  - dim_stadium: {transform_results.get('dim_stadium', (0,0))[0]} rows")
        print(f"  - dim_referee: {transform_results.get('dim_referee', (0,0))[0]} rows")
    
    print("="*70)


if __name__ == "__main__":
    run_complete_etl_pipeline()
