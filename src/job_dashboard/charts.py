"""Chart factories for dashboard visualizations."""

import matplotlib.pyplot as plt
import pandas as pd


def _bar_chart(series: pd.Series, title: str, figsize: tuple[int, int] = (8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    series.plot(kind="bar", ax=ax)
    ax.set_ylabel("Count")
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def _line_chart(series: pd.Series, title: str, figsize: tuple[int, int] = (9, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    series.plot(kind="line", marker="o", ax=ax)
    ax.set_ylabel("Count")
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def categories_chart(series: pd.Series):
    return _bar_chart(series, "Top Job Categories")


def locations_chart(series: pd.Series):
    return _bar_chart(series, "Top Candidate Locations")


def companies_chart(series: pd.Series):
    return _bar_chart(series, "Top Companies")


def salary_chart(series: pd.Series):
    return _bar_chart(series, "Jobs With Salary Info", figsize=(6, 4))


def skills_chart(series: pd.Series):
    return _bar_chart(series, "Top Skills Mentioned in Titles")


def jobs_over_time_chart(series: pd.Series):
    return _line_chart(series, "Jobs Over Time")


def top_skills_over_time_chart(series: pd.Series):
    return _bar_chart(series, "Top Skills Across Snapshots")


def top_companies_over_time_chart(series: pd.Series):
    return _bar_chart(series, "Top Companies Across Snapshots")


def top_categories_over_time_chart(series: pd.Series):
    return _bar_chart(series, "Top Categories Across Snapshots")
