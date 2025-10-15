"""Configuration and constants for ETL.
Reads connection info from environment variables.
"""
import os

DATABASE = {
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "1234"),
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": os.getenv("MYSQL_PORT", "3307"),
    "db": os.getenv("MYSQL_DB", "epl_dw"),
}

def database_url():
    """
    Constructs the SQLAlchemy database URL for a MySQL connection.
    Uses the 'mysql+mysqlconnector' dialect.
    """

    # NOTE: You may need to install the 'mysql-connector-python' package (pip install mysql-connector-python)
    return f"mysql+mysqlconnector://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['db']}"

# Other constants
RAW_DATA_DIR = "data/raw"
STAGING_DIR = "data/staging"