"""Simple API client placeholders."""
import requests


def fetch_json(url, params=None, timeout=10):
    """Fetch JSON from a URL and return parsed dict or raise.
    """
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
