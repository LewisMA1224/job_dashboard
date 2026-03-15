import pandas as pd

from src.job_dashboard.processing import (
    add_skill_column,
    clean_jobs,
    extract_skills,
    infer_posted_recency,
    normalize_company,
)


def test_clean_jobs_enriches_expected_columns():
    publication_date = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=2)).isoformat()
    jobs = [
        {
            "id": "abc123",
            "title": "Senior Backend Python Engineer",
            "description": "Build APIs using Python and AWS",
            "company_name": "Acme, Inc.",
            "category": "Software Development",
            "job_type": "Full-time",
            "publication_date": publication_date,
            "candidate_required_location": "Worldwide",
            "salary": "$120k",
            "url": "https://example.com/job/1",
        }
    ]

    df = clean_jobs(jobs)
    df = add_skill_column(df)

    assert len(df) == 1
    assert df.loc[0, "seniority_level"] == "senior"
    assert df.loc[0, "role_family"] in {"backend", "data", "devops", "other"}
    assert df.loc[0, "remote_scope"] == "worldwide"
    assert df.loc[0, "posted_recency"] == "this_week"
    assert df.loc[0, "normalized_company"] == "acme inc"
    assert df.loc[0, "salary_present"] == "Yes"
    assert "python" in df.loc[0, "detected_skills"]


def test_normalize_company_handles_empty():
    assert normalize_company("") == "unknown"
    assert normalize_company("  Foo-Bar LLC ") == "foobar llc"


def test_extract_skills_uses_title_and_description():
    skills = extract_skills("Backend Engineer", "Uses Python, Docker, and AWS")

    assert "python" in skills
    assert "docker" in skills
    assert "aws" in skills


def test_infer_posted_recency_unknown_for_invalid_date():
    assert infer_posted_recency("not-a-date") == "unknown"
