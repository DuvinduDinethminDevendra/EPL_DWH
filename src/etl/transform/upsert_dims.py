"""Upsert helpers for slowly-changing dimensions.

This module contains simple patterns that can be adapted for SCD Type 1/2.
"""
from sqlalchemy import text


def upsert_dim(engine, table_name, df, key_columns):
    """Naive upsert placeholder: deletes matching keys then inserts.
    Not suitable for production SCD logic; replace with proper SQL or SQLAlchemy models.
    """
    with engine.begin() as conn:
        for _, row in df.iterrows():
            where_clause = " AND ".join([f"{k} = :{k}" for k in key_columns])
            delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            params = {k: row[k] for k in key_columns}
            conn.execute(text(delete_sql), params)
        # bulk insert via pandas or COPY is recommended; left as an exercise
    return True
