"""Snapshot persistence and historical trend utilities.

This module uses CSV for simplicity and portability in a portfolio project.
CSV keeps setup friction low while still enabling historical trend analysis.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import SNAPSHOT_CSV_PATH

SNAPSHOT_COLUMNS = [
    "fetch_timestamp",
    "fetch_date",
    "stable_job_key",
    "job_id",
    "title",
    "company",
    "normalized_company",
    "category",
    "candidate_required_location",
    "salary_present",
    "seniority_level",
    "role_family",
    "remote_scope",
    "posted_recency",
    "detected_skills_str",
    "url",
]


def _serialize_skills(skills: object) -> str:
    if isinstance(skills, list):
        return ";".join(
            sorted({str(skill).lower() for skill in skills if str(skill).strip()})
        )
    return ""


def _deserialize_skills(skills_str: str) -> list[str]:
    return [part for part in str(skills_str).split(";") if part]


def _snapshot_path(path: str | None = None) -> Path:
    return Path(path or SNAPSHOT_CSV_PATH)


def prepare_snapshot(
    df: pd.DataFrame, fetch_timestamp: pd.Timestamp | None = None
) -> pd.DataFrame:
    """Build snapshot rows from enriched jobs dataframe."""
    if df.empty:
        return pd.DataFrame(columns=SNAPSHOT_COLUMNS)

    fetch_ts = fetch_timestamp or pd.Timestamp.now(tz="UTC")
    snapshot = df.copy()
    snapshot["fetch_timestamp"] = fetch_ts.isoformat()
    snapshot["fetch_date"] = fetch_ts.date().isoformat()
    snapshot["detected_skills_str"] = snapshot["detected_skills"].apply(
        _serialize_skills
    )

    snapshot = snapshot[
        [
            "fetch_timestamp",
            "fetch_date",
            "stable_job_key",
            "job_id",
            "title",
            "company",
            "normalized_company",
            "category",
            "candidate_required_location",
            "salary_present",
            "seniority_level",
            "role_family",
            "remote_scope",
            "posted_recency",
            "detected_skills_str",
            "url",
        ]
    ]

    return snapshot.drop_duplicates(
        subset=["fetch_date", "stable_job_key"]
    ).reset_index(drop=True)


def save_snapshot(df: pd.DataFrame, path: str | None = None) -> dict[str, int]:
    """Append snapshot rows to CSV while avoiding duplicates per day/job key."""
    snapshot_df = prepare_snapshot(df)
    if snapshot_df.empty:
        return {"inserted": 0, "total": 0}

    target_path = _snapshot_path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        existing = pd.read_csv(target_path)
    else:
        existing = pd.DataFrame(columns=SNAPSHOT_COLUMNS)

    combined = pd.concat([existing, snapshot_df], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["fetch_date", "stable_job_key"], keep="last"
    )
    combined.to_csv(target_path, index=False)

    return {"inserted": max(len(combined) - len(existing), 0), "total": len(combined)}


def load_snapshot_history(path: str | None = None) -> pd.DataFrame:
    target_path = _snapshot_path(path)
    if not target_path.exists():
        return pd.DataFrame(columns=SNAPSHOT_COLUMNS)

    history = pd.read_csv(target_path)
    if "detected_skills_str" not in history.columns:
        history["detected_skills_str"] = ""

    history["detected_skills"] = (
        history["detected_skills_str"].fillna("").apply(_deserialize_skills)
    )
    return history


def build_trend_summary(history_df: pd.DataFrame) -> dict[str, pd.Series]:
    """Generate basic trend outputs from historical snapshots."""
    if history_df.empty:
        empty = pd.Series(dtype=int)
        return {
            "job_count_over_time": empty,
            "top_companies_over_time": empty,
            "top_skills_over_time": empty,
            "top_categories_over_time": empty,
        }

    job_count_over_time = (
        history_df.groupby("fetch_date")["stable_job_key"].nunique().sort_index()
    )

    top_companies = history_df["normalized_company"].value_counts().head(10)
    top_categories = history_df["category"].value_counts().head(10)

    all_skills: list[str] = []
    for skills in history_df["detected_skills"]:
        all_skills.extend(skills)

    top_skills = (
        pd.Series(all_skills).value_counts().head(10)
        if all_skills
        else pd.Series(dtype=int)
    )

    return {
        "job_count_over_time": job_count_over_time,
        "top_companies_over_time": top_companies,
        "top_skills_over_time": top_skills,
        "top_categories_over_time": top_categories,
    }
