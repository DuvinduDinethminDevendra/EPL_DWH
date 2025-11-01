#!/usr/bin/env python
"""Test loading a single StatsBomb match to verify the date enrichment fix."""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.etl.db import get_engine
from src.etl.extract.statsbomb_reader import load_events_from_file, get_epl_events_files
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    engine = get_engine()
    
    # Get first EPL event file
    event_files = get_epl_events_files()
    if not event_files:
        print("No event files found")
        sys.exit(1)
    
    print(f"[OK] Found {len(event_files)} event files")
    
    # Load just the first one
    first_file = event_files[0]
    print(f"[OK] Testing with first file: {first_file.name}")
    
    events_loaded = load_events_from_file(first_file, engine)
    print(f"[OK] Loaded {events_loaded} events")
    
    # Check if they were inserted
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM stg_events_raw"))
        count = result.scalar()
        print(f"[OK] stg_events_raw now has {count} rows")
        
        # Show a sample
        result = conn.execute(text("SELECT event_id, match_date FROM stg_events_raw LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"[OK] Sample event: ID={row[0]}, match_date={row[1]}")

except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    sys.exit(1)
