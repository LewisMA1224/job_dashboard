"""Data cleaning and feature engineering for jobs data."""

from __future__ import annotations

import hashlib
import re

import pandas as pd

from .config import (
    REMOTE_SCOPE_KEYWORDS,
    ROLE_FAMILY_KEYWORDS,
    SENIORITY_KEYWORDS,
    SKILL_KEYWORDS,
)


def _safe_text(value: object) -> str:
    return str(value or "").strip()


def _normalized_text(value: object) -> str:
    return re.sub(r"\s+", " ", _safe_text(value).lower())


def _keyword_match(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def normalize_company(company: str) -> str:
    """Normalize company name for stable grouping.

    Assumption: simple normalization (case-fold + punctuation trimming) is enough for
    portfolio MVP grouping even if it won't merge all legal-entity variations.
    """
    cleaned = _normalized_text(company)
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    return cleaned or "unknown"


def infer_seniority_level(title: str, description: str) -> str:
    text = _normalized_text(f"{title} {description}")
    for label in ["intern", "junior", "mid", "senior", "staff", "lead", "principal"]:
        if _keyword_match(text, SENIORITY_KEYWORDS[label]):
            return label
    return "unknown"


def infer_role_family(title: str, description: str, category: str) -> str:
    text = _normalized_text(f"{title} {description} {category}")
    for family, keywords in ROLE_FAMILY_KEYWORDS.items():
        if _keyword_match(text, keywords):
            return family
    return "other"


def infer_remote_scope(location_text: str) -> str:
    text = _normalized_text(location_text)
    for scope in ["worldwide", "us-only", "europe-only"]:
        if _keyword_match(text, REMOTE_SCOPE_KEYWORDS[scope]):
            return scope
    return "unknown"


def infer_posted_recency(publication_date: object) -> str:
    published = pd.to_datetime(publication_date, errors="coerce", utc=True)
    if pd.isna(published):
        return "unknown"

    now_utc = pd.Timestamp.now(tz="UTC")
    days_old = (now_utc - published).days
    if days_old <= 0:
        return "today"
    if days_old <= 7:
        return "this_week"
    return "older"


def clean_jobs(jobs: list[dict]) -> pd.DataFrame:
    """Normalize API payload into an analysis-ready DataFrame."""
    rows = []

    for job in jobs:
        description = _safe_text(job.get("description"))
        title = _safe_text(job.get("title"))
        company = _safe_text(job.get("company_name"))
        location_text = _safe_text(job.get("candidate_required_location"))
        salary_text = _safe_text(job.get("salary"))
        publication_date = job.get("publication_date")

        stable_key_source = "|".join(
            [
                _safe_text(job.get("id")),
                _safe_text(job.get("url")),
                title,
                company,
            ]
        )
        stable_job_key = hashlib.sha1(stable_key_source.encode("utf-8")).hexdigest()

        rows.append(
            {
                "job_id": job.get("id"),
                "stable_job_key": stable_job_key,
                "title": title,
                "description": description,
                "company": company,
                "normalized_company": normalize_company(company),
                "category": _safe_text(job.get("category")) or "Unknown",
                "job_type": _safe_text(job.get("job_type")) or "Unknown",
                "publication_date": publication_date,
                "candidate_required_location": location_text or "Unknown",
                "salary": salary_text,
                "salary_present": "Yes" if salary_text else "No",
                "url": _safe_text(job.get("url")),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["title"] = df["title"].fillna("").str.strip()
    df["description"] = df["description"].fillna("").str.strip()
    df["company"] = df["company"].fillna("").str.strip()
    df["normalized_company"] = df["normalized_company"].fillna("unknown")
    df["category"] = df["category"].fillna("Unknown").str.strip()
    df["job_type"] = df["job_type"].fillna("Unknown").str.strip()
    df["candidate_required_location"] = (
        df["candidate_required_location"].fillna("Unknown").str.strip()
    )
    df["salary"] = df["salary"].fillna("").astype(str).str.strip()
    df["salary_present"] = df["salary_present"].fillna("No")

    df["seniority_level"] = df.apply(
        lambda row: infer_seniority_level(row["title"], row["description"]),
        axis=1,
    )
    df["role_family"] = df.apply(
        lambda row: infer_role_family(
            row["title"], row["description"], row["category"]
        ),
        axis=1,
    )
    df["remote_scope"] = df["candidate_required_location"].apply(infer_remote_scope)
    df["posted_recency"] = df["publication_date"].apply(infer_posted_recency)

    # Compatibility alias keeps old dashboards/scripts working while new code
    # uses salary_present.
    df["has_salary"] = df["salary_present"]

    return df


def extract_skills(title: str, description: str = "") -> list[str]:
    """Infer skill tokens from title and description text."""
    full_text = _normalized_text(f"{title} {description}")
    return [skill for skill in SKILL_KEYWORDS if skill in full_text]


def add_skill_column(df: pd.DataFrame) -> pd.DataFrame:
    """Attach detected skills list to each row."""
    if df.empty:
        return df

    result = df.copy()
    result["detected_skills"] = result.apply(
        lambda row: extract_skills(row["title"], row.get("description", "")),
        axis=1,
    )

    # Compatibility alias for existing summary code paths.
    result["skills"] = result["detected_skills"]
    return result
