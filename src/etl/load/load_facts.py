"""Bulk load facts into the warehouse."""


def load_facts(engine, df, table_name, if_exists="append"):
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return True
