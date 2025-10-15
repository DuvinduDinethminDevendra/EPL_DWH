"""CSV reading helpers using pandas."""
import pandas as pd
from pathlib import Path


def read_csv(path, **kwargs):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(p, **kwargs)
