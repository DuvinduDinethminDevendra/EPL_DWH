#!/usr/bin/env python3
"""Run StatsBomb extractor and report completion."""

import sys
import logging
from datetime import datetime

from src.etl.extract.statsbomb_reader import fetch_and_load_statsbomb_events

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STARTING STATSBOMB EVENT EXTRACTION")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        success = fetch_and_load_statsbomb_events()
        
        print("\n" + "=" * 70)
        print("EXTRACTION FINISHED")
        print("=" * 70)
        print(f"Result: {'✓ SUCCESS' if success else '⚠ PARTIAL/FAILED'}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
