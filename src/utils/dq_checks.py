"""Simple data quality checks for pandas DataFrames."""

def check_non_nulls(df, cols):
    missing = {c: int(df[c].isna().sum()) for c in cols if c in df.columns}
    return missing
