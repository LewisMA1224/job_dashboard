import matplotlib.figure
import pandas as pd

from src.job_dashboard.charts import (
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


def test_chart_factories_return_matplotlib_figures():
    bar_series = pd.Series([5, 3], index=["A", "B"])
    line_series = pd.Series([2, 4, 6], index=["2026-03-13", "2026-03-14", "2026-03-15"])

    figs = [
        categories_chart(bar_series),
        companies_chart(bar_series),
        locations_chart(bar_series),
        salary_chart(bar_series),
        skills_chart(bar_series),
        jobs_over_time_chart(line_series),
        top_skills_over_time_chart(bar_series),
        top_companies_over_time_chart(bar_series),
        top_categories_over_time_chart(bar_series),
    ]

    assert all(isinstance(fig, matplotlib.figure.Figure) for fig in figs)
