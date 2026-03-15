import pandas as pd

from src.job_dashboard.filters import apply_filters, build_filter_options, build_summary


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "title": "Senior Backend Engineer",
                "description": "python api docker",
                "company": "Acme",
                "normalized_company": "acme",
                "category": "Software Development",
                "candidate_required_location": "Worldwide",
                "salary_present": "Yes",
                "seniority_level": "senior",
                "role_family": "backend",
                "detected_skills": ["python", "docker"],
                "remote_scope": "worldwide",
                "posted_recency": "this_week",
            },
            {
                "title": "Junior Data Analyst",
                "description": "sql pandas",
                "company": "Beta",
                "normalized_company": "beta",
                "category": "Data",
                "candidate_required_location": "USA",
                "salary_present": "No",
                "seniority_level": "junior",
                "role_family": "data",
                "detected_skills": ["sql", "pandas"],
                "remote_scope": "us-only",
                "posted_recency": "older",
            },
        ]
    )


def test_apply_filters_include_exclude_and_salary():
    df = _sample_df()

    filtered = apply_filters(
        df,
        {
            "search_term": "",
            "apply_local_search": False,
            "include_keywords": "engineer",
            "include_match_mode": "OR",
            "exclude_keywords": "junior",
            "company": [],
            "category": [],
            "location": [],
            "salary_present": "Yes",
            "seniority_level": [],
            "role_family": [],
            "detected_skills": [],
            "remote_scope": [],
            "posted_recency": [],
        },
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["company"] == "Acme"


def test_apply_filters_skill_and_company_multiselect():
    df = _sample_df()

    filtered = apply_filters(
        df,
        {
            "search_term": "",
            "apply_local_search": False,
            "include_keywords": "",
            "include_match_mode": "OR",
            "exclude_keywords": "",
            "company": ["Beta"],
            "category": [],
            "location": [],
            "salary_present": "All",
            "seniority_level": [],
            "role_family": [],
            "detected_skills": ["sql"],
            "remote_scope": [],
            "posted_recency": [],
        },
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["title"] == "Junior Data Analyst"


def test_build_filter_options_and_summary():
    df = _sample_df()
    options = build_filter_options(df)
    summary = build_summary(df)

    assert "Acme" in options["company"]
    assert "backend" in options["role_family"]
    assert "python" in options["detected_skills"]
    assert int(summary["salary_counts"].sum()) == len(df)
    assert "acme" in summary["top_companies"].index


def test_include_keywords_or_mode_is_default_broad():
    df = _sample_df()

    filtered = apply_filters(
        df,
        {
            "search_term": "",
            "apply_local_search": False,
            "include_keywords": "engineer,analyst",
            "include_match_mode": "OR",
            "exclude_keywords": "",
            "company": [],
            "category": [],
            "location": [],
            "salary_present": "All",
            "seniority_level": [],
            "role_family": [],
            "detected_skills": [],
            "remote_scope": [],
            "posted_recency": [],
        },
    )

    assert len(filtered) == 2


def test_include_keywords_and_mode_is_strict():
    df = _sample_df()

    filtered = apply_filters(
        df,
        {
            "search_term": "",
            "apply_local_search": False,
            "include_keywords": "senior,backend,engineer",
            "include_match_mode": "AND",
            "exclude_keywords": "",
            "company": [],
            "category": [],
            "location": [],
            "salary_present": "All",
            "seniority_level": [],
            "role_family": [],
            "detected_skills": [],
            "remote_scope": [],
            "posted_recency": [],
        },
    )

    assert len(filtered) == 1
    assert filtered.iloc[0]["title"] == "Senior Backend Engineer"
