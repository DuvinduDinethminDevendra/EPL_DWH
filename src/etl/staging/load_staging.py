"""Functions to write staging tables.

These are simple wrappers around pandas.to_sql for development.
"""
from ..db import get_engine


def write_staging(df, table_name, if_exists="replace"):
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return True
