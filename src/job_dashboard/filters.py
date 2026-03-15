"""Filtering and aggregation logic for the dashboard."""

from __future__ import annotations

import pandas as pd


def _parse_keywords(value: str) -> list[str]:
    return [part.strip().lower() for part in str(value).split(",") if part.strip()]


def apply_title_filter(df: pd.DataFrame, title_filter: str) -> pd.DataFrame:
    """Backward-compatible include keyword filter for titles."""
    keywords = _parse_keywords(title_filter)
    if df.empty or not keywords:
        return df

    pattern = "|".join(keywords)
    return df[df["title"].str.lower().str.contains(pattern, na=False)]


def apply_filters(df: pd.DataFrame, filters: dict[str, object]) -> pd.DataFrame:
    """Apply all dashboard filters in a deterministic sequence."""
    filtered_df, _ = apply_filters_with_debug(df, filters)
    return filtered_df


def apply_filters_with_debug(
    df: pd.DataFrame, filters: dict[str, object]
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Apply filters and return per-step row counts for debugging UX."""
    debug_steps: list[dict[str, object]] = []

    def _record_step(name: str, before_count: int, after_count: int) -> None:
        debug_steps.append(
            {
                "step": name,
                "rows_before": before_count,
                "rows_after": after_count,
                "rows_removed": before_count - after_count,
            }
        )

    if df.empty:
        _record_step("initial_rows", 0, 0)
        return df, debug_steps

    result = df.copy()
    _record_step("initial_rows", len(result), len(result))

    apply_local_search = bool(filters.get("apply_local_search", False))
    search_term = str(filters.get("search_term", "")).strip().lower()
    if search_term and apply_local_search:
        before_count = len(result)
        combined = (
            result["title"].fillna("").str.lower()
            + " "
            + result["description"].fillna("").str.lower()
        )
        result = result[combined.str.contains(search_term, na=False)]
        _record_step("local_search", before_count, len(result))

    include_match_mode = str(filters.get("include_match_mode", "OR")).upper()
    include_keywords = _parse_keywords(str(filters.get("include_keywords", "")))
    if include_keywords:
        before_count = len(result)
        title_series = result["title"].fillna("").str.lower()
        if include_match_mode == "AND":
            for keyword in include_keywords:
                result = result[title_series.str.contains(keyword, na=False)]
                title_series = result["title"].fillna("").str.lower()
            _record_step("include_keywords_and", before_count, len(result))
        else:
            include_pattern = "|".join(include_keywords)
            result = result[
                result["title"].str.lower().str.contains(include_pattern, na=False)
            ]
            _record_step("include_keywords_or", before_count, len(result))

    exclude_keywords = _parse_keywords(str(filters.get("exclude_keywords", "")))
    if exclude_keywords:
        before_count = len(result)
        exclude_pattern = "|".join(exclude_keywords)
        result = result[
            ~result["title"].str.lower().str.contains(exclude_pattern, na=False)
        ]
        _record_step("exclude_keywords", before_count, len(result))

    company_values = [str(value) for value in filters.get("company", [])]
    if company_values:
        before_count = len(result)
        result = result[result["company"].isin(company_values)]
        _record_step("company", before_count, len(result))

    category_values = [str(value) for value in filters.get("category", [])]
    if category_values:
        before_count = len(result)
        result = result[result["category"].isin(category_values)]
        _record_step("category", before_count, len(result))

    location_values = [str(value) for value in filters.get("location", [])]
    if location_values:
        before_count = len(result)
        result = result[result["candidate_required_location"].isin(location_values)]
        _record_step("location", before_count, len(result))

    salary_present = str(filters.get("salary_present", "All"))
    if salary_present in {"Yes", "No"}:
        before_count = len(result)
        result = result[result["salary_present"] == salary_present]
        _record_step("salary_present", before_count, len(result))

    seniority_values = [str(value) for value in filters.get("seniority_level", [])]
    if seniority_values:
        before_count = len(result)
        result = result[result["seniority_level"].isin(seniority_values)]
        _record_step("seniority_level", before_count, len(result))

    role_family_values = [str(value) for value in filters.get("role_family", [])]
    if role_family_values:
        before_count = len(result)
        result = result[result["role_family"].isin(role_family_values)]
        _record_step("role_family", before_count, len(result))

    skill_values = [str(value).lower() for value in filters.get("detected_skills", [])]
    if skill_values and "detected_skills" in result.columns:
        before_count = len(result)
        result = result[
            result["detected_skills"].apply(
                lambda skills: any(skill in set(skills) for skill in skill_values)
            )
        ]
        _record_step("detected_skills", before_count, len(result))

    remote_scope_values = [str(value) for value in filters.get("remote_scope", [])]
    if remote_scope_values:
        before_count = len(result)
        result = result[result["remote_scope"].isin(remote_scope_values)]
        _record_step("remote_scope", before_count, len(result))

    posted_recency_values = [str(value) for value in filters.get("posted_recency", [])]
    if posted_recency_values:
        before_count = len(result)
        result = result[result["posted_recency"].isin(posted_recency_values)]
        _record_step("posted_recency", before_count, len(result))

    _record_step("final_rows", len(result), len(result))
    return result, debug_steps


def build_filter_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """Return unique option lists for sidebar controls."""
    if df.empty:
        return {
            "company": [],
            "category": [],
            "location": [],
            "seniority_level": [],
            "role_family": [],
            "detected_skills": [],
            "remote_scope": [],
            "posted_recency": [],
        }

    skill_values: list[str] = []
    if "detected_skills" in df.columns:
        for skills in df["detected_skills"]:
            skill_values.extend(skills)

    return {
        "company": sorted(
            [value for value in df["company"].dropna().unique() if value]
        ),
        "category": sorted(
            [value for value in df["category"].dropna().unique() if value]
        ),
        "location": sorted(
            [
                value
                for value in df["candidate_required_location"].dropna().unique()
                if value
            ]
        ),
        "seniority_level": sorted(
            [value for value in df["seniority_level"].dropna().unique() if value]
        ),
        "role_family": sorted(
            [value for value in df["role_family"].dropna().unique() if value]
        ),
        "detected_skills": sorted(set(skill_values)),
        "remote_scope": sorted(
            [value for value in df["remote_scope"].dropna().unique() if value]
        ),
        "posted_recency": sorted(
            [value for value in df["posted_recency"].dropna().unique() if value]
        ),
    }


def build_summary(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Build all chart-ready summary series in one place."""
    if df.empty:
        return {
            "top_categories": pd.Series(dtype=int),
            "top_locations": pd.Series(dtype=int),
            "top_companies": pd.Series(dtype=int),
            "salary_counts": pd.Series(dtype=int),
            "top_skills": pd.Series(dtype=int),
        }

    skill_list = []
    for skills in df["detected_skills"]:
        skill_list.extend(skills)

    skills_series = pd.Series(skill_list)

    return {
        "top_categories": df["category"].value_counts().head(10),
        "top_locations": df["candidate_required_location"].value_counts().head(10),
        "top_companies": df["normalized_company"].value_counts().head(10),
        "salary_counts": df["salary_present"].value_counts(),
        "top_skills": (
            skills_series.value_counts().head(10)
            if not skills_series.empty
            else pd.Series(dtype=int)
        ),
    }
