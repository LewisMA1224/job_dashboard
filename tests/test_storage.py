import pandas as pd

from src.job_dashboard.storage import (
    build_trend_summary,
    load_snapshot_history,
    save_snapshot,
)


def _snapshot_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "stable_job_key": "k1",
                "job_id": "1",
                "title": "Senior Backend Engineer",
                "company": "Acme",
                "normalized_company": "acme",
                "category": "Software Development",
                "candidate_required_location": "Worldwide",
                "salary_present": "Yes",
                "seniority_level": "senior",
                "role_family": "backend",
                "remote_scope": "worldwide",
                "posted_recency": "this_week",
                "detected_skills": ["python", "docker"],
                "url": "https://example.com/1",
            },
            {
                "stable_job_key": "k2",
                "job_id": "2",
                "title": "Data Analyst",
                "company": "Beta",
                "normalized_company": "beta",
                "category": "Data",
                "candidate_required_location": "USA",
                "salary_present": "No",
                "seniority_level": "junior",
                "role_family": "data",
                "remote_scope": "us-only",
                "posted_recency": "older",
                "detected_skills": ["sql"],
                "url": "https://example.com/2",
            },
        ]
    )


def test_save_snapshot_deduplicates_by_day_and_key(tmp_path):
    path = tmp_path / "snapshots.csv"
    df = _snapshot_df()

    first = save_snapshot(df, str(path))
    second = save_snapshot(df, str(path))

    assert first["inserted"] == 2
    assert second["inserted"] == 0

    history = load_snapshot_history(str(path))
    assert len(history) == 2


def test_build_trend_summary_from_history(tmp_path):
    path = tmp_path / "snapshots.csv"
    df = _snapshot_df()
    save_snapshot(df, str(path))

    history = load_snapshot_history(str(path))
    trends = build_trend_summary(history)

    assert not trends["job_count_over_time"].empty
    assert "acme" in trends["top_companies_over_time"].index
    assert "python" in trends["top_skills_over_time"].index
