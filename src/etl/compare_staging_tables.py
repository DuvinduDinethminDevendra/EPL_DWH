"""Script to compare stg_team_raw and stg_player_raw staging tables.
Prints schema differences and data statistics.
"""
import subprocess
import json

def run_mysql_query(query):
    """Run MySQL query and return result."""
    cmd = f'docker exec epl_mysql mysql -u root -p1234 epl_dw -e "{query}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def compare_staging_tables():
    """Compare stg_team_raw and stg_player_raw tables."""
    
    print("\n" + "="*80)
    print("STAGING TABLES COMPARISON: stg_team_raw vs stg_player_raw")
    print("="*80 + "\n")
    
    # Get column info for both tables
    team_schema = run_mysql_query("DESC stg_team_raw;")
    player_schema = run_mysql_query("DESC stg_player_raw;")
    
    # Parse schemas
    team_cols = {}
    for line in team_schema.strip().split('\n')[1:]:
        parts = line.split()
        if len(parts) >= 2:
            team_cols[parts[0]] = ' '.join(parts[1:])
    
    player_cols = {}
    for line in player_schema.strip().split('\n')[1:]:
        parts = line.split()
        if len(parts) >= 2:
            player_cols[parts[0]] = ' '.join(parts[1:])
    
    # Print column comparison
    print("COLUMN STRUCTURE:")
    print("-" * 80)
    
    common_cols = set(team_cols.keys()) & set(player_cols.keys())
    only_in_team = set(team_cols.keys()) - set(player_cols.keys())
    only_in_player = set(player_cols.keys()) - set(team_cols.keys())
    
    print(f"\nCOMMON COLUMNS ({len(common_cols)}):")
    for col in sorted(common_cols):
        team_type = team_cols[col]
        player_type = player_cols[col]
        match = "OK" if team_type == player_type else "DIFFERENT"
        print(f"  • {col:30} | team: {team_type:30} | player: {player_type:30}")
    
    print(f"\nONLY IN stg_team_raw ({len(only_in_team)}):")
    for col in sorted(only_in_team):
        print(f"  • {col:30} | {team_cols[col]}")
    
    print(f"\nONLY IN stg_player_raw ({len(only_in_player)}):")
    for col in sorted(only_in_player):
        print(f"  • {col:30} | {player_cols[col]}")
    
    # Get data statistics
    print("\n" + "="*80)
    print("DATA STATISTICS:")
    print("-" * 80)
    
    team_count = run_mysql_query("SELECT COUNT(*) FROM stg_team_raw;").strip().split('\n')[1]
    player_count = run_mysql_query("SELECT COUNT(*) FROM stg_player_raw;").strip().split('\n')[1]
    
    print(f"stg_team_raw:     {team_count:>10} records")
    print(f"stg_player_raw:   {player_count:>10} records")
    
    # Get status distribution
    print(f"\nstg_team_raw Status Distribution:")
    team_status = run_mysql_query("SELECT COALESCE(status, 'NULL') as status, COUNT(*) as count FROM stg_team_raw GROUP BY status;")
    for line in team_status.strip().split('\n')[1:]:
        if line:
            parts = line.split()
            print(f"  {parts[0]:15} : {parts[1]:>10}")
    
    print(f"\nstg_player_raw Status Distribution:")
    player_status = run_mysql_query("SELECT COALESCE(status, 'NULL') as status, COUNT(*) as count FROM stg_player_raw GROUP BY status;")
    for line in player_status.strip().split('\n')[1:]:
        if line:
            parts = line.split()
            print(f"  {parts[0]:15} : {parts[1]:>10}")
    
    # Get audit fields summary
    print("\nAudit Fields Summary:")
    
    team_audit = run_mysql_query("SELECT COUNT(DISTINCT YEAR(load_start_time)) as years FROM stg_team_raw;")
    player_audit = run_mysql_query("SELECT COUNT(DISTINCT season) as seasons FROM stg_player_raw;")
    
    team_years = team_audit.strip().split('\n')[1]
    player_seasons = player_audit.strip().split('\n')[1]
    
    print(f"  stg_team_raw Unique Years:    {team_years}")
    print(f"  stg_player_raw Unique Seasons: {player_seasons}")
    
    # Get sample record
    print("\n" + "="*80)
    print("SAMPLE RECORDS (first row):")
    print("-" * 80)
    
    print("\nstg_team_raw:")
    team_sample = run_mysql_query("SELECT * FROM stg_team_raw LIMIT 1;")
    print(team_sample[:500] + ("..." if len(team_sample) > 500 else ""))
    
    print("\nstg_player_raw:")
    player_sample = run_mysql_query("SELECT * FROM stg_player_raw LIMIT 1;")
    print(player_sample[:500] + ("..." if len(player_sample) > 500 else ""))
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    compare_staging_tables()
