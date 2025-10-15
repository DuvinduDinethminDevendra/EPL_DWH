"""Configuration and constants for ETL.
Reads connection info from environment variables.
"""
import os

DATABASE = {
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "db": os.getenv("POSTGRES_DB", "epl_dw"),
}

def database_url():
    return f"postgresql+psycopg2://{DATABASE['root']}:{DATABASE['1234']}@{DATABASE['localhost']}:{DATABASE['3307']}/{DATABASE['epl_dw']}"

# Other constants
RAW_DATA_DIR = "data/raw"
STAGING_DIR = "data/staging"
