"""StatsBomb Open Data events extractor.

Downloads and extracts StatsBomb open data events from GitHub, then loads them into staging table.
StatsBomb provides free event-level data for historical EPL matches (3 seasons).

Repository: https://github.com/statsbomb/open-data
Structure: Each match is one JSON file under data/events/

Usage:
    from extract_statsbomb_events import fetch_and_load_statsbomb_events
    fetch_and_load_statsbomb_events()
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from ..db import get_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# StatsBomb repository details
STATSBOMB_REPO = "https://github.com/statsbomb/open-data.git"
STATSBOMB_LOCAL_PATH = None  # Will be set to data/statsbomb_open

def _get_statsbomb_path() -> Path:
    """Get StatsBomb repository path (supports both git clone and downloaded ZIP).
    
    Looks for:
    1. data/raw/open-data-master (extracted from ZIP)
    2. data/raw/statsbomb_open (from git clone)
    
    Returns:
        Path to the statsbomb repository root
    """
    global STATSBOMB_LOCAL_PATH
    if STATSBOMB_LOCAL_PATH is None:
        project_root = Path(__file__).resolve().parents[3]
        
        # Try open-data-master first (from ZIP download)
        master_path = project_root / "data" / "raw" / "open-data-master"
        if master_path.exists():
            logger.info(f"✓ Using open-data-master repository at {master_path}")
            STATSBOMB_LOCAL_PATH = master_path
        else:
            # Fallback to statsbomb_open (from git clone)
            STATSBOMB_LOCAL_PATH = project_root / "data" / "raw" / "statsbomb_open"
    
    return STATSBOMB_LOCAL_PATH


def clone_or_update_statsbomb_repo() -> bool:
    """Clone or update StatsBomb open data repository.
    
    Returns:
        True if successful, False otherwise
    """
    statsbomb_path = _get_statsbomb_path()
    
    try:
        if statsbomb_path.exists():
            logger.info(f"✓ StatsBomb repo exists at: {statsbomb_path}")
            logger.info("Updating repository from GitHub...")
            
            try:
                os.chdir(str(statsbomb_path))
                result = subprocess.run(
                    ["git", "pull"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    logger.info(f"✓ Repository updated successfully")
                    logger.info(f"  Output: {result.stdout.strip() if result.stdout else 'Up to date'}")
                    return True
            except subprocess.TimeoutExpired:
                logger.error("Git pull timed out (>300s). Network issue?")
                return False
            except subprocess.CalledProcessError as e:
                logger.error(f"Git pull failed with error: {e.stderr}")
                return False
        else:
            logger.info(f"StatsBomb repo NOT found at: {statsbomb_path}")
            logger.info(f"Creating parent directories...")
            
            try:
                statsbomb_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Directories created")
            except Exception as e:
                logger.error(f"Failed to create directories: {e}")
                return False
            
            logger.info(f"Cloning repository from GitHub...")
            logger.info(f"  Source: {STATSBOMB_REPO}")
            logger.info(f"  Destination: {statsbomb_path}")
            
            try:
                result = subprocess.run(
                    ["git", "clone", STATSBOMB_REPO, str(statsbomb_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                logger.info(f"✓ Repository cloned successfully")
                logger.info(f"  Output: {result.stdout.strip() if result.stdout else 'Clone complete'}")
                return True
            except subprocess.TimeoutExpired:
                logger.error("Git clone timed out (>600s). Large repo + slow connection?")
                logger.error(f"Partial clone may exist at: {statsbomb_path}")
                return False
            except subprocess.CalledProcessError as e:
                logger.error(f"Git clone failed with error: {e.stderr}")
                logger.error(f"Ensure git is installed and GitHub is reachable")
                return False
    
    except FileNotFoundError as e:
        logger.error(f"Git command not found. Please install git: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error managing StatsBomb repo: {e}")
        return False


def get_epl_events_files() -> List[Path]:
    """Find all EPL match event JSON files from StatsBomb repository.
    
    Supports both repository formats:
    - open-data-master/data/events/ (ZIP extraction)
    - data/events/ (git clone)
    
    Returns:
        List of Path objects pointing to event JSON files
    """
    statsbomb_path = _get_statsbomb_path()
    
    # Standard StatsBomb event location
    events_path = statsbomb_path / "data" / "events"
    
    if events_path.exists():
        event_files = sorted(events_path.glob("*.json"))
        if event_files:
            logger.info(f"✓ Found {len(event_files)} EPL event JSON files")
            logger.info(f"  Location: {events_path}")
            return event_files
        else:
            logger.warning(f"Events directory exists but is empty: {events_path}")
    else:
        logger.error(f"Events directory not found at: {events_path}")
    
    # Fallback: search entire data/raw for JSON files
    logger.info(f"Attempting fallback: searching entire data/raw directory...")
    fallback_root = statsbomb_path.parent
    event_files = sorted([f for f in fallback_root.rglob("*.json")])
    
    if event_files:
        logger.info(f"⚠  Found {len(event_files)} JSON files via fallback search")
        logger.info(f"  (This may include non-event JSONs)")
        return event_files
    
    logger.error(f"No JSON files found anywhere in: {fallback_root}")
    return []


def parse_statsbomb_event(event: Dict[str, Any], match_id: int) -> Dict[str, Any]:
    """Parse a StatsBomb event JSON object into staging columns.
    
    Args:
        event: Raw StatsBomb event dict
        match_id: StatsBomb match ID (for linking)
    
    Returns:
        Dictionary with staging table columns
    """
    try:
        # Extract nested objects safely
        player = event.get("player", {})
        team = event.get("team", {})
        position = event.get("position", {})
        location = event.get("location", [])
        
        # Get event type
        event_type = event.get("type", {})
        type_name = event_type.get("name", "OTHER") if isinstance(event_type, dict) else str(event_type)
        
        # Extract specific action data based on type
        pass_data = event.get("pass", {})
        shot_data = event.get("shot", {})
        duel_data = event.get("duel", {})
        carry_data = event.get("carry", {})
        
        return {
            "event_id": event.get("id"),
            "statsbomb_match_id": match_id,
            "statsbomb_period": event.get("period"),
            "timestamp": event.get("timestamp"),
            "minute": event.get("minute"),
            "second": event.get("second"),
            "type": type_name,
            "player_name": player.get("name") if isinstance(player, dict) else None,
            "player_id": player.get("id") if isinstance(player, dict) else None,
            "team_name": team.get("name") if isinstance(team, dict) else None,
            "team_id": team.get("id") if isinstance(team, dict) else None,
            "position": position.get("name") if isinstance(position, dict) else None,
            "possession_team_name": event.get("possession_team", {}).get("name") if isinstance(event.get("possession_team"), dict) else None,
            "play_pattern": event.get("play_pattern", {}).get("name") if isinstance(event.get("play_pattern"), dict) else None,
            "tactics_formation": event.get("tactics", {}).get("formation") if isinstance(event.get("tactics"), dict) else None,
            "carry_end_location": json.dumps(carry_data.get("end_location")) if carry_data.get("end_location") else None,
            "pass_recipient_name": pass_data.get("recipient", {}).get("name") if isinstance(pass_data.get("recipient"), dict) else None,
            "pass_length": pass_data.get("length"),
            "shot_outcome": shot_data.get("outcome", {}).get("name") if isinstance(shot_data.get("outcome"), dict) else None,
            "shot_xg": shot_data.get("xg"),
            "duel_outcome": duel_data.get("outcome", {}).get("name") if isinstance(duel_data.get("outcome"), dict) else None,
            "raw_data": json.dumps(event),
            "status": "LOADED"
        }
    except Exception as e:
        logger.warning(f"Error parsing event {event.get('id')}: {e}")
        return None


def load_events_from_file(file_path: Path, engine) -> int:
    """Load all events from a single StatsBomb match JSON file.
    
    Args:
        file_path: Path to the JSON file
        engine: SQLAlchemy engine
    
    Returns:
        Number of events loaded
    """
    try:
        # Match ID is the filename (without .json)
        match_id = int(file_path.stem)
        
        # Check if already processed
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM ETL_Events_Manifest WHERE statsbomb_match_id = :match_id"),
                {"match_id": match_id}
            )
            if result.scalar() > 0:
                logger.info(f"  ✓ Match {match_id} already processed, skipping")
                return 0
        
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            match_events = json.load(f)
        
        if not isinstance(match_events, list):
            logger.warning(f"Match {match_id}: Expected list of events, got {type(match_events)}")
            return 0
        
        logger.info(f"  Processing match {match_id}: {len(match_events)} events")
        
        # Parse all events
        parsed_events = []
        for event in match_events:
            parsed = parse_statsbomb_event(event, match_id)
            if parsed:
                parsed_events.append(parsed)
        
        if not parsed_events:
            logger.warning(f"  No events parsed from match {match_id}")
            return 0
        
        # Bulk insert into staging table
        df = pd.DataFrame(parsed_events)
        rows_inserted = df.to_sql(
            "stg_events_raw",
            engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500
        )
        
        # Record in manifest
        load_end = datetime.now()
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO ETL_Events_Manifest 
                    (statsbomb_match_id, file_name, file_path, load_start_time, load_end_time, status, rows_processed)
                    VALUES (:match_id, :file_name, :file_path, :load_start, :load_end, 'SUCCESS', :rows)
                """),
                {
                    "match_id": match_id,
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "load_start": datetime.now(),
                    "load_end": load_end,
                    "rows": len(parsed_events)
                }
            )
            conn.commit()
        
        logger.info(f"  ✓ Loaded {len(parsed_events)} events from match {match_id}")
        return len(parsed_events)
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error loading events from {file_path}: {e}")
        return 0


def fetch_and_load_statsbomb_events() -> bool:
    """Main orchestration function.
    
    Steps:
    1. Clone/update StatsBomb repository
    2. Find all EPL event JSON files
    3. Load each into stg_events_raw
    4. Record manifest entries
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("="*70)
    logger.info("STATSBOMB EVENTS EXTRACTION & STAGING")
    logger.info("="*70)
    
    try:
        engine = get_engine()
        
        # Step 1: Clone or update repo (best-effort). If cloning fails, fall back to local files under data/raw
        logger.info("\n[Step 1/3] Clone/update StatsBomb repository (best-effort)...")
        if not clone_or_update_statsbomb_repo():
            logger.warning("Clone/update failed — will attempt to locate existing local JSON files under data/raw")
            # do not return; proceed to scanning local directories
        
        # Step 2: Find event files
        logger.info("\n[Step 2/3] Scanning for EPL event files...")
        event_files = get_epl_events_files()
        
        if not event_files:
            logger.error("No event files found in StatsBomb repository")
            return False
        
        logger.info(f"Found {len(event_files)} event files")
        
        # Step 3: Load all events
        logger.info("\n[Step 3/3] Loading events into staging table...")
        total_events = 0
        failed_files = 0
        
        for idx, event_file in enumerate(event_files, 1):
            try:
                events_loaded = load_events_from_file(event_file, engine)
                total_events += events_loaded
            except Exception as e:
                logger.error(f"Failed to load {event_file}: {e}")
                failed_files += 1
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("STATSBOMB LOADING SUMMARY")
        logger.info("="*70)
        logger.info(f"Total files processed: {len(event_files)}")
        logger.info(f"Total events loaded: {total_events}")
        logger.info(f"Failed files: {failed_files}")
        logger.info(f"Status: {'✓ SUCCESS' if failed_files == 0 else '⚠ PARTIAL'}")
        logger.info("="*70 + "\n")
        
        return failed_files == 0
    
    except Exception as e:
        logger.error(f"Fatal error in fetch_and_load_statsbomb_events: {e}")
        return False


if __name__ == "__main__":
    success = fetch_and_load_statsbomb_events()
    exit(0 if success else 1)
