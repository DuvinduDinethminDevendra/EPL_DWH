import json
import logging
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from ..db import get_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JSONReader:
    def __init__(self, json_dir: str):
        self.json_dir = Path(json_dir)
        self.engine = get_engine()
        logger.info(f"JSON Reader initialized - checking manifest for already-scanned files")
    
    def _get_processed_files(self):
        """Get set of files already processed from manifest"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT file_path FROM ETL_JSON_Manifest WHERE status='SUCCESS'"))
            return {row[0] for row in result}
    
    def read_json_files(self):
        """Read all JSON files from nested season folders (e.g., Season_1992/Arsenal_FC_11_1992.json)"""
        # Recursively find all .json files in subdirectories
        json_files = list(self.json_dir.glob('*/*.json'))  # Season_YYYY/TeamName_*.json
        logger.info(f"Found {len(json_files)} JSON files across all season folders")
        
        if not json_files:
            logger.warning(f"No JSON files found in {self.json_dir}")
            return
        
        # Get already-processed files
        processed = self._get_processed_files()
        logger.info(f"Already processed: {len(processed)} files")
        
        skipped = 0
        for json_file in json_files:
            file_key = f"{json_file.parent.name}/{json_file.name}"
            if file_key in processed:
                skipped += 1
                continue
            self._process_json_file(json_file)
        
        if skipped > 0:
            logger.info(f"⊘ Skipped {skipped} already-processed files")
    
    def _process_json_file(self, file_path: Path):
        """Process individual JSON file and extract individual players"""
        load_start_time = datetime.now()
        total_rows = 0
        error_msg = None
        status = 'SUCCESS'
        file_key = f"{file_path.parent.name}/{file_path.name}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract season from parent folder name (e.g., "Season_1992" -> 1992)
            season_folder = file_path.parent.name  # e.g., "Season_1992"
            try:
                season_year = int(season_folder.split('_')[1])
            except (IndexError, ValueError):
                season_year = None
            
            # Get team ID from the top-level "id" field
            team_id = data.get('id')
            
            # Extract players from the "players" array
            players = data.get('players', [])
            if not isinstance(players, list):
                players = [players]
            
            # Insert each individual player into staging table
            with self.engine.connect() as conn:
                for player in players:
                    player_id = player.get('id')
                    
                    if not player_id:
                        continue
                    
                    # Use filename as file_name, full path as file_path
                    sql = text('''
                        INSERT INTO stg_player_raw 
                        (file_name, file_path, season, load_start_time, status, 
                         rows_processed, player_id, player_name, team, position, raw_data, created_at)
                        VALUES (:file_name, :file_path, :season, :load_start_time, 'PENDING',
                                1, :player_id, :player_name, :team, :position, :raw_data, :created_at)
                    ''')
                    conn.execute(sql, {
                        'file_name': file_path.name,
                        'file_path': file_key,
                        'season': season_year,
                        'load_start_time': load_start_time,
                        'player_id': player_id,
                        'player_name': player.get('name'),
                        'team': team_id,
                        'position': player.get('position'),
                        'raw_data': json.dumps(player),
                        'created_at': datetime.now()
                    })
                    total_rows += 1
                
                # Update all rows to mark load completion
                load_end_time = datetime.now()
                update_sql = text('''
                    UPDATE stg_player_raw 
                    SET status = :status, 
                        load_end_time = :load_end_time,
                        rows_processed = :rows_processed
                    WHERE file_name = :file_name 
                      AND file_path = :file_path
                      AND status = 'PENDING'
                ''')
                conn.execute(update_sql, {
                    'status': 'SUCCESS',
                    'load_end_time': load_end_time,
                    'rows_processed': total_rows,
                    'file_name': file_path.name,
                    'file_path': file_key
                })
                
                # Log to manifest so we skip next time
                manifest_sql = text('''
                    INSERT INTO ETL_JSON_Manifest (file_name, file_path, season, load_start_time, load_end_time, status, rows_processed)
                    VALUES (:file_name, :file_path, :season, :load_start_time, :load_end_time, :status, :rows_processed)
                ''')
                conn.execute(manifest_sql, {
                    'file_name': file_path.name,
                    'file_path': file_key,
                    'season': season_year,
                    'load_start_time': load_start_time,
                    'load_end_time': load_end_time,
                    'status': 'SUCCESS',
                    'rows_processed': total_rows
                })
                conn.commit()
            
            logger.info(f"✓ Loaded {total_rows} records from {file_key}")
        
        except Exception as e:
            logger.error(f"✗ Error processing {file_key}: {e}")
            status = 'FAILED'
            error_msg = str(e)
            
            # Log error to manifest
            try:
                with self.engine.connect() as conn:
                    manifest_sql = text('''
                        INSERT INTO ETL_JSON_Manifest (file_name, file_path, season, load_start_time, load_end_time, status, rows_processed, error_message)
                        VALUES (:file_name, :file_path, :season, :load_start_time, :load_end_time, :status, :rows_processed, :error_message)
                    ''')
                    conn.execute(manifest_sql, {
                        'file_name': file_path.name,
                        'file_path': file_key,
                        'season': season_year,
                        'load_start_time': load_start_time,
                        'load_end_time': datetime.now(),
                        'status': status,
                        'rows_processed': total_rows if total_rows > 0 else None,
                        'error_message': error_msg
                    })
                    conn.commit()
            except Exception as log_error:
                logger.error(f"Failed to log error: {log_error}")
    
    def close(self):
        """Cleanup database resources"""
        self.engine.dispose()

if __name__ == '__main__':
    json_reader = JSONReader('data/raw/json')
    json_reader.read_json_files()
    json_reader.close()
    logger.info("✓ ETL process completed")