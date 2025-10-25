#!/usr/bin/env python3
"""Analyze StatsBomb repository structure and find EPL matches."""

import json
from pathlib import Path

# Load competitions
comp_file = Path("data/raw/open-data-master/data/competitions.json")
with open(comp_file) as f:
    comps = json.load(f)

epl_comps = [c for c in comps if c.get("competition_id") == 2]
print("=" * 60)
print("EPL COMPETITIONS")
print("=" * 60)
for c in sorted(epl_comps, key=lambda x: x.get("season_id", 0)):
    print(f"  Season ID {c['season_id']}: {c['season_name']}")

# Check available match files
matches_dir = Path("data/raw/open-data-master/data/matches/2")
match_files = sorted([f.stem for f in matches_dir.glob("*.json") if f.stem.isdigit()])
print(f"\n{'=' * 60}")
print("AVAILABLE MATCH FILES (data/matches/2/)")
print("=" * 60)
print(f"Season JSON files: {match_files}")

# Load each and count matches
print(f"\n{'=' * 60}")
print("EPL MATCH COUNT")
print("=" * 60)
total_epl_matches = 0
match_ids = set()
for season_id in match_files:
    season_file = matches_dir / f"{season_id}.json"
    with open(season_file) as f:
        matches = json.load(f)
    count = len(matches)
    total_epl_matches += count
    match_ids.update([m["match_id"] for m in matches])
    print(f"  Season {season_id}: {count:4d} matches")

print(f"\n{'=' * 60}")
print("SUMMARY")
print("=" * 60)
print(f"Total unique match_ids: {len(match_ids)}")

events_dir = Path("data/raw/open-data-master/data/events")
events_count = len(list(events_dir.glob("*.json")))
print(f"Total event JSON files available: {events_count}")

# Check if all match_ids have event files
missing_events = set()
for mid in sorted(match_ids):
    event_file = events_dir / f"{mid}.json"
    if not event_file.exists():
        missing_events.add(mid)

if missing_events:
    print(f"\n⚠  Missing event files for {len(missing_events)} matches:")
    print(f"   {sorted(missing_events)[:10]}...")
else:
    print(f"\n✓ All {len(match_ids)} EPL matches have event files!")

print(f"\n{'=' * 60}")
print("EVENT DATA LOCATION")
print("=" * 60)
print(f"Event files: {events_dir}")
print(f"Ready to load {len(match_ids)} EPL match events")
