"""Streamlit UI composition for the remote jobs dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .api import fetch_jobs
from .charts import (
    categories_chart,
    companies_chart,
    jobs_over_time_chart,
    locations_chart,
    salary_chart,
    skills_chart,
    top_categories_over_time_chart,
    top_companies_over_time_chart,
    top_skills_over_time_chart,
)
from .config import (
    DEFAULT_EXCLUDE_KEYWORDS,
    DEFAULT_SEARCH_TERM,
    DEFAULT_TITLE_KEYWORDS,
)
from .filters import apply_filters_with_debug, build_filter_options, build_summary
from .processing import add_skill_column, clean_jobs
from .storage import build_trend_summary, load_snapshot_history, save_snapshot


@st.cache_data
def fetch_jobs_cached(search_term: str) -> list[dict]:
    """Streamlit-cached wrapper around API client calls."""
    return fetch_jobs(search_term)


def _init_session_state() -> None:
    if "base_df" not in st.session_state:
        st.session_state.base_df = pd.DataFrame()

    defaults = {
        "search_term": DEFAULT_SEARCH_TERM,
        "include_keywords": DEFAULT_TITLE_KEYWORDS,
        "exclude_keywords": DEFAULT_EXCLUDE_KEYWORDS,
        "include_strict_mode": False,
        "apply_local_search": False,
        "company_filter": [],
        "category_filter": [],
        "location_filter": [],
        "salary_filter": "All",
        "seniority_filter": [],
        "role_family_filter": [],
        "skills_filter": [],
        "remote_scope_filter": [],
        "posted_recency_filter": [],
        "last_fetch_count": 0,
        "last_snapshot_inserted": 0,
        "last_snapshot_total": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_filters() -> None:
    st.session_state.include_keywords = DEFAULT_TITLE_KEYWORDS
    st.session_state.exclude_keywords = DEFAULT_EXCLUDE_KEYWORDS
    st.session_state.include_strict_mode = False
    st.session_state.apply_local_search = False
    st.session_state.company_filter = []
    st.session_state.category_filter = []
    st.session_state.location_filter = []
    st.session_state.salary_filter = "All"
    st.session_state.seniority_filter = []
    st.session_state.role_family_filter = []
    st.session_state.skills_filter = []
    st.session_state.remote_scope_filter = []
    st.session_state.posted_recency_filter = []


def _build_filter_payload() -> dict[str, object]:
    return {
        "search_term": st.session_state.search_term,
        "include_keywords": st.session_state.include_keywords,
        "exclude_keywords": st.session_state.exclude_keywords,
        "include_match_mode": "AND" if st.session_state.include_strict_mode else "OR",
        "apply_local_search": st.session_state.apply_local_search,
        "company": st.session_state.company_filter,
        "category": st.session_state.category_filter,
        "location": st.session_state.location_filter,
        "salary_present": st.session_state.salary_filter,
        "seniority_level": st.session_state.seniority_filter,
        "role_family": st.session_state.role_family_filter,
        "detected_skills": st.session_state.skills_filter,
        "remote_scope": st.session_state.remote_scope_filter,
        "posted_recency": st.session_state.posted_recency_filter,
    }


def render_app() -> None:
    """Render the full dashboard UI."""
    st.set_page_config(page_title="Remote Job Market Dashboard", layout="wide")
    _init_session_state()

    st.title("Remote Job Market Tracker")
    st.write(
        "Track remote market signals with enriched job intelligence and historical snapshots."
    )

    st.sidebar.header("Data Controls")
    st.sidebar.text_input(
        "Primary Search Term",
        key="search_term",
        help="Used for API fetch. Keep blank for broad, cross-market results.",
    )

    if st.sidebar.button("Fetch Latest Jobs", use_container_width=True):
        jobs = fetch_jobs_cached(st.session_state.search_term)
        base_df = add_skill_column(clean_jobs(jobs))
        snapshot_result = save_snapshot(base_df)
        st.session_state.base_df = base_df
        st.session_state.last_fetch_count = len(jobs)
        st.session_state.last_snapshot_inserted = snapshot_result["inserted"]
        st.session_state.last_snapshot_total = snapshot_result["total"]

    st.sidebar.caption(
        f"Last fetch: {st.session_state.last_fetch_count} jobs | "
        f"Snapshot rows added: {st.session_state.last_snapshot_inserted}"
    )

    st.sidebar.header("Filters")
    st.sidebar.text_input(
        "Include Title Keywords",
        key="include_keywords",
        help="Comma-separated keywords. OR logic by default.",
    )
    st.sidebar.checkbox(
        "Strict Include Mode (AND)",
        key="include_strict_mode",
        help="If enabled, title must contain all include keywords.",
    )
    st.sidebar.text_input(
        "Exclude Title Keywords",
        key="exclude_keywords",
        help="Comma-separated keywords. Jobs containing these are removed.",
    )
    st.sidebar.checkbox(
        "Apply Local Search Filter",
        key="apply_local_search",
        help="Off by default to avoid double filtering after API search.",
    )

    base_df = st.session_state.base_df
    if base_df.empty:
        st.info("No data loaded yet. Use the sidebar and click Fetch Latest Jobs.")
        return

    options = build_filter_options(base_df)

    st.sidebar.multiselect("Company", options["company"], key="company_filter")
    st.sidebar.multiselect("Category", options["category"], key="category_filter")
    st.sidebar.multiselect("Location", options["location"], key="location_filter")
    st.sidebar.selectbox(
        "Salary Present",
        options=["All", "Yes", "No"],
        key="salary_filter",
    )
    st.sidebar.multiselect(
        "Seniority Level", options["seniority_level"], key="seniority_filter"
    )
    st.sidebar.multiselect(
        "Role Family", options["role_family"], key="role_family_filter"
    )
    st.sidebar.multiselect(
        "Detected Skills", options["detected_skills"], key="skills_filter"
    )
    st.sidebar.multiselect(
        "Remote Scope", options["remote_scope"], key="remote_scope_filter"
    )
    st.sidebar.multiselect(
        "Posted Recency", options["posted_recency"], key="posted_recency_filter"
    )

    if st.sidebar.button("Reset Filters", use_container_width=True):
        _reset_filters()
        st.rerun()

    if st.button(
        "Clear All Filters", help="Resets all local filters to broad defaults."
    ):
        _reset_filters()
        st.rerun()

    filtered_df, debug_steps = apply_filters_with_debug(
        base_df, _build_filter_payload()
    )

    st.subheader("Overview")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Jobs", len(filtered_df))
    kpi2.metric("Jobs With Salary", int((filtered_df["salary_present"] == "Yes").sum()))
    kpi3.metric("Unique Companies", filtered_df["company"].nunique())
    kpi4.metric("Unique Categories", filtered_df["category"].nunique())

    if filtered_df.empty:
        st.warning("No jobs matched the current filters. Adjust filters or reset them.")
        st.subheader("Filter Debug")
        st.dataframe(pd.DataFrame(debug_steps), use_container_width=True)
        return

    st.subheader("Filter Debug")
    st.caption("Row counts after each active filtering step.")
    st.dataframe(pd.DataFrame(debug_steps), use_container_width=True)

    summary = build_summary(filtered_df)

    st.subheader("Filtered Jobs")
    st.dataframe(
        filtered_df[
            [
                "title",
                "company",
                "category",
                "seniority_level",
                "role_family",
                "candidate_required_location",
                "remote_scope",
                "posted_recency",
                "salary_present",
                "salary",
                "url",
            ]
        ],
        use_container_width=True,
    )

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered CSV",
        data=csv_data,
        file_name="remote_jobs_filtered_export.csv",
        mime="text/csv",
    )

    st.subheader("Job Details")
    job_choices = filtered_df.reset_index(drop=True)
    selected_index = st.selectbox(
        "Select a row for detail",
        options=list(job_choices.index),
        format_func=lambda idx: f"{job_choices.loc[idx, 'title']} | {job_choices.loc[idx, 'company']}",
    )
    selected_job = job_choices.loc[selected_index]
    with st.expander("Selected Job Details", expanded=False):
        st.write(f"Title: {selected_job['title']}")
        st.write(f"Company: {selected_job['company']}")
        st.write(f"Category: {selected_job['category']}")
        st.write(f"Seniority: {selected_job['seniority_level']}")
        st.write(f"Role Family: {selected_job['role_family']}")
        st.write(f"Location: {selected_job['candidate_required_location']}")
        st.write(f"Remote Scope: {selected_job['remote_scope']}")
        st.write(f"Posted Recency: {selected_job['posted_recency']}")
        st.write(f"Salary Present: {selected_job['salary_present']}")
        st.write(f"Salary: {selected_job['salary']}")
        st.write(f"URL: {selected_job['url']}")
        st.write(
            f"Detected Skills: {', '.join(selected_job['detected_skills']) or 'None'}"
        )

    st.subheader("Current Snapshot Analytics")
    st.pyplot(categories_chart(summary["top_categories"]))
    st.pyplot(locations_chart(summary["top_locations"]))
    st.pyplot(companies_chart(summary["top_companies"]))
    st.pyplot(salary_chart(summary["salary_counts"]))

    if summary["top_skills"].empty:
        st.info("No skills detected in the current filtered result set.")
    else:
        st.pyplot(skills_chart(summary["top_skills"]))

    st.subheader("Historical Trends")
    history_df = load_snapshot_history()
    trends = build_trend_summary(history_df)

    if history_df.empty:
        st.info(
            "No historical snapshots yet. Fetch data to start building trends over time."
        )
        return

    st.caption(f"Snapshot rows stored: {len(history_df)}")
    if not trends["job_count_over_time"].empty:
        st.pyplot(jobs_over_time_chart(trends["job_count_over_time"]))

    trend_col1, trend_col2 = st.columns(2)
    with trend_col1:
        if trends["top_skills_over_time"].empty:
            st.info("No historical skill data available yet.")
        else:
            st.pyplot(top_skills_over_time_chart(trends["top_skills_over_time"]))
    with trend_col2:
        if trends["top_companies_over_time"].empty:
            st.info("No historical company data available yet.")
        else:
            st.pyplot(top_companies_over_time_chart(trends["top_companies_over_time"]))

    if not trends["top_categories_over_time"].empty:
        st.pyplot(top_categories_over_time_chart(trends["top_categories_over_time"]))
