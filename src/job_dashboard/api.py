"""API client module for remote jobs data."""

import requests

from .config import API_URL


def fetch_jobs(search_term: str) -> list[dict]:
    """Fetch jobs from the Remotive API for the given search term."""
    params = {"search": search_term}
    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data.get("jobs", [])
