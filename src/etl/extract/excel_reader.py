"""
Excel Reader Module
Extracts data from Excel files in the data/raw/xlsx folder
Supports referee, stadium, and other dimension data
"""

import os
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy import text
from ..db import get_engine

logger = logging.getLogger(__name__)

class ExcelReader:
    """Reads Excel files from data/raw/xlsx and loads into staging tables"""
    
    def __init__(self):
        self.xlsx_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "xlsx"
        self.engine = get_engine()
        
    def get_excel_files(self) -> List[Path]:
        """Get all Excel files from xlsx directory"""
        if not self.xlsx_dir.exists():
            logger.warning(f"xlsx directory does not exist: {self.xlsx_dir}")
            return []
        
        excel_files = list(self.xlsx_dir.glob("*.xlsx")) + list(self.xlsx_dir.glob("*.xls"))
        logger.info(f"Found {len(excel_files)} Excel files in {self.xlsx_dir}")
        return excel_files
    
    def check_manifest(self, file_name: str) -> bool:
        """Check if file has already been processed"""
        query = """
            SELECT 1 FROM ETL_Excel_Manifest 
            WHERE file_name = :file_name AND status = 'SUCCESS'
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query), {"file_name": file_name})
            return result.fetchone() is not None
    
    def log_manifest(self, file_name: str, file_path: str, sheet_name: str, 
                     data_type: str, status: str, rows_processed: int = 0, 
                     error_message: str = None):
        """Log file load to ETL_Excel_Manifest"""
        query = """
            INSERT INTO ETL_Excel_Manifest 
            (file_name, file_path, sheet_name, data_type, load_start_time, 
             load_end_time, status, rows_processed, error_message)
            VALUES (:file_name, :file_path, :sheet_name, :data_type, :load_start_time, 
                    :load_end_time, :status, :rows_processed, :error_message)
        """
        with self.engine.connect() as conn:
            conn.execute(text(query), {
                "file_name": file_name,
                "file_path": str(file_path),
                "sheet_name": sheet_name,
                "data_type": data_type,
                "load_start_time": datetime.now(),
                "load_end_time": datetime.now(),
                "status": status,
                "rows_processed": rows_processed,
                "error_message": error_message
            })
            conn.commit()
    
    def load_referee_data(self, file_path: Path) -> Tuple[int, str]:
        """Load referee data from Excel into stg_referee_raw"""
        try:
            logger.info(f"Loading referee data from {file_path.name}")
            
            # Check if already processed
            if self.check_manifest(file_path.name):
                logger.info(f"File {file_path.name} already processed, skipping")
                return 0, "SKIPPED"
            
            # Read Excel file - try to find the right sheet
            xls = pd.ExcelFile(file_path)
            sheet_name = None
            
            # Look for a sheet with 'referee' in the name
            for sheet in xls.sheet_names:
                if 'referee' in sheet.lower():
                    sheet_name = sheet
                    break
            
            if not sheet_name:
                # If not found, use the first sheet (excluding Sheet1)
                for sheet in xls.sheet_names:
                    if sheet != 'Sheet1':
                        sheet_name = sheet
                        break
            
            if not sheet_name:
                error_msg = "Could not find appropriate sheet for referee data"
                logger.error(error_msg)
                self.log_manifest(file_path.name, file_path, 'Unknown', 'Referee', 'FAILED', 0, error_msg)
                return 0, f"FAILED: {error_msg}"
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if df.empty:
                logger.warning(f"No data found in {file_path.name}")
                self.log_manifest(file_path.name, file_path, sheet_name, 'Referee', 'EMPTY', 0)
                return 0, "EMPTY"
            
            # Insert into staging table using SQLAlchemy
            df_insert = df.copy()
            df_insert['file_name'] = file_path.name
            df_insert['load_start_time'] = datetime.now()
            df_insert['status'] = 'LOADED'
            
            # Log available columns for debugging
            logger.info(f"Columns found in {sheet_name}: {list(df.columns)}")
            
            # Map column names to match database schema (case-insensitive)
            column_mapping = {}
            df_lower_cols = {col.lower(): col for col in df.columns}
            
            # Map all expected columns
            expected_mappings = {
                'referee_name': 'referee_name',
                'date_of_birth': 'date_of_birth',
                'birth_date': 'date_of_birth',
                'birth': 'date_of_birth',
                'dob': 'date_of_birth',
                'nationality': 'nationality',
                'premier_league_debut': 'premier_league_debut',
                'pl_debut': 'premier_league_debut',
                'debut': 'premier_league_debut',
                'status': 'ref_status',
                'notes': 'notes'
            }
            
            for excel_col, db_col in expected_mappings.items():
                if excel_col in df_lower_cols:
                    original_col = df_lower_cols[excel_col]
                    column_mapping[original_col] = db_col
                    logger.info(f"Mapped column: {original_col} → {db_col}")
            
            df_insert = df_insert.rename(columns=column_mapping)
            
            # Ensure all required columns exist (fill with None if missing)
            required_cols = ['referee_name', 'date_of_birth', 'nationality', 
                           'premier_league_debut', 'ref_status', 'notes',
                           'file_name', 'load_start_time', 'status']
            for col in required_cols:
                if col not in df_insert.columns:
                    df_insert[col] = None
            
            df_insert.to_sql('stg_referee_raw', self.engine, if_exists='append', index=False)
            
            rows_inserted = len(df)
            logger.info(f"Loaded {rows_inserted} referee records from {file_path.name}")
            self.log_manifest(file_path.name, file_path, sheet_name, 'Referee', 'SUCCESS', rows_inserted)
            return rows_inserted, "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading referee data from {file_path.name}: {error_msg}")
            try:
                self.log_manifest(file_path.name, file_path, 'Unknown', 'Referee', 'FAILED', 0, error_msg)
            except:
                pass  # Ignore if manifest logging fails
            return 0, f"FAILED: {error_msg}"
    
    def load_stadium_data(self, file_path: Path) -> Tuple[int, str]:
        """Load stadium data from Excel into dim_stadium"""
        try:
            logger.info(f"Loading stadium data from {file_path.name}")
            
            if self.check_manifest(file_path.name):
                logger.info(f"File {file_path.name} already processed, skipping")
                return 0, "SKIPPED"
            
            # Read Excel file - try to find the right sheet
            xls = pd.ExcelFile(file_path)
            sheet_name = None
            
            # Look for a sheet with 'stadium' in the name
            for sheet in xls.sheet_names:
                if 'stadium' in sheet.lower():
                    sheet_name = sheet
                    break
            
            if not sheet_name:
                # If not found, use the first sheet (excluding Sheet1)
                for sheet in xls.sheet_names:
                    if sheet != 'Sheet1':
                        sheet_name = sheet
                        break
            
            if not sheet_name:
                error_msg = "Could not find appropriate sheet for stadium data"
                logger.error(error_msg)
                self.log_manifest(file_path.name, file_path, 'Unknown', 'Stadium', 'FAILED', 0, error_msg)
                return 0, f"FAILED: {error_msg}"
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if df.empty:
                logger.warning(f"No data found in {file_path.name}")
                self.log_manifest(file_path.name, file_path, sheet_name, 'Stadium', 'EMPTY', 0)
                return 0, "EMPTY"
            
            # Map column names to match database schema (case-insensitive)
            column_mapping = {}
            df_lower_cols = {col.lower(): col for col in df.columns}
            
            if 'stadium_name' in df_lower_cols or 'name' in df_lower_cols:
                for key in ['stadium_name', 'name']:
                    if key in df_lower_cols:
                        column_mapping[df_lower_cols[key]] = 'stadium_name'
                        break
            if 'capacity' in df_lower_cols:
                column_mapping[df_lower_cols['capacity']] = 'capacity'
            if 'city' in df_lower_cols:
                column_mapping[df_lower_cols['city']] = 'city'
            
            df_insert = df.rename(columns=column_mapping)
            
            # Insert into dimension table
            df_insert.to_sql('dim_stadium', self.engine, if_exists='append', index=False)
            
            rows_inserted = len(df)
            logger.info(f"Loaded {rows_inserted} stadium records from {file_path.name}")
            self.log_manifest(file_path.name, file_path, sheet_name, 'Stadium', 'SUCCESS', rows_inserted)
            return rows_inserted, "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error loading stadium data from {file_path.name}: {error_msg}")
            try:
                self.log_manifest(file_path.name, file_path, 'Unknown', 'Stadium', 'FAILED', 0, error_msg)
            except:
                pass  # Ignore if manifest logging fails
            return 0, f"FAILED: {error_msg}"
    
    def process_all_excel_files(self) -> Dict[str, Tuple[int, str]]:
        """Process all Excel files in the xlsx directory"""
        results = {}
        excel_files = self.get_excel_files()
        
        if not excel_files:
            logger.info("No Excel files found to process")
            return results
        
        for file_path in excel_files:
            file_name = file_path.name.lower()
            
            if 'referee' in file_name:
                rows, status = self.load_referee_data(file_path)
                results[file_name] = (rows, status)
            elif 'stadium' in file_name:
                rows, status = self.load_stadium_data(file_path)
                results[file_name] = (rows, status)
            else:
                logger.warning(f"Unknown Excel file type: {file_name}")
        
        return results
    
    def close(self):
        """Close database connection"""
        # SQLAlchemy engine connections are managed automatically
        pass


def load_excel_data() -> Dict[str, Tuple[int, str]]:
    """Main function to load Excel data"""
    reader = ExcelReader()
    try:
        logger.info("Starting Excel data extraction...")
        results = reader.process_all_excel_files()
        logger.info(f"Excel extraction completed with {len(results)} files processed")
        return results
    finally:
        reader.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = load_excel_data()
    for file_name, (rows, status) in results.items():
        print(f"{file_name}: {rows} rows, {status}")
