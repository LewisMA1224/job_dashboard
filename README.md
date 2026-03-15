# Remote Job Market Tracker

A modular Streamlit MVP that tracks remote hiring signals from live API data, enriches jobs with market-intelligence features, and stores historical snapshots for trend analysis.

## Project Overview

Remote Job Market Tracker helps job seekers and data-focused developers answer practical questions such as:

- Which companies are hiring remotely right now?
- Which role families are rising in demand?
- Which skills appear most often across snapshots over time?

The app is structured as a clean, portfolio-ready analytics project with separation between data access, enrichment, filtering, persistence, charting, and UI.

## Why This App Exists

Most simple job dashboards only display current listings. This project moves beyond that by:

- Enriching raw jobs into useful features (seniority, role family, remote scope, skill detection)
- Supporting multi-dimensional filtering in the UI
- Persisting daily snapshots to enable trend analysis over time

This makes the app closer to a real product MVP rather than a one-off visualization script.

## Features

### Data Intelligence

- `seniority_level` inferred from title + description
- `role_family` classification (backend, frontend, fullstack, data, devops, etc.)
- `detected_skills` from title + description keyword scanning
- `remote_scope` inference from location text
- `posted_recency` bucketing (`today`, `this_week`, `older`, `unknown`)
- `normalized_company` for cleaner grouping
- `salary_present` standardized yes/no signal

### Filtering

- Search term filter
- Include title keywords (comma-separated)
- Exclude title keywords (comma-separated)
- Company, category, and location filters
- Salary presence filter
- Seniority, role family, remote scope, posted recency filters
- Detected skills multi-select filter

### UX and Analytics

- Sidebar control panel
- Reset filters button
- KPI cards
- Filtered jobs table + CSV export
- Selected job detail expander
- Current snapshot charts
- Historical trend charts from stored snapshots

### Snapshot Persistence

- CSV-based snapshot storage (`data/job_snapshots.csv`)
- Fetch timestamp + fetch date per snapshot row
- Duplicate reduction using `fetch_date + stable_job_key`
- Trend outputs over saved history

## Tech Stack

- Python 3.10+
- Streamlit
- Requests
- Pandas
- Matplotlib
- Pytest

## Architecture / Folder Structure

```text
python-web-scraping/
|-- job_dashboard_app.py
|-- src/
|   |-- job_dashboard/
|   |   |-- __init__.py
|   |   |-- api.py            # API fetching
|   |   |-- charts.py         # Chart factories (current + historical)
|   |   |-- config.py         # Constants, defaults, keyword maps
|   |   |-- filters.py        # Filtering and summary aggregations
|   |   |-- processing.py     # Cleaning and enrichment logic
|   |   |-- storage.py        # Snapshot persistence + trend builders
|   |   |-- ui.py             # Streamlit orchestration
|-- tests/
|   |-- test_api.py
|   |-- test_processing.py
|   |-- test_filters.py
|   |-- test_charts.py
|   |-- test_storage.py
|-- assets/
|   |-- screenshots/          # Portfolio images and static chart assets
|-- archive/
|   |-- sandbox/              # Legacy scripts and sandbox artifacts
|-- data/
|   |-- job_snapshots.csv     # Runtime snapshot history (local by default)
|-- README.md
```

## Data Flow

```text
Streamlit sidebar inputs
        |
        v
Remotive API fetch (api.py)
        |
        v
Cleaning + enrichment (processing.py)
- seniority_level
- role_family
- detected_skills
- remote_scope
- posted_recency
        |
        v
Snapshot persistence (storage.py)
- append to data/job_snapshots.csv
- dedupe by fetch_date + stable_job_key
        |
        v
Filter pipeline (filters.py)
        |
        v
Summary aggregations (filters.py + storage.py)
        |
        v
Charts + UI rendering (charts.py + ui.py)
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip

### Install

1. Clone repository:

```bash
git clone <your-repo-url>
cd python-web-scraping
```

2. Create virtual environment:

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install streamlit requests pandas matplotlib pytest
```

## How To Run Locally

Run the Streamlit app:

```bash
streamlit run job_dashboard_app.py
```

Open the URL shown in terminal (commonly `http://localhost:8501`).

## Testing Instructions

Run the full test suite:

```bash
pytest -q
```

## Screenshots (Placeholders)

Use `assets/screenshots/` for visuals and add the following assets:

```markdown
![Tracker Overview](assets/screenshots/tracker-overview.png)
![Sidebar Filters](assets/screenshots/sidebar-filters.png)
![Historical Trends](assets/screenshots/historical-trends.png)
![Job Detail Panel](assets/screenshots/job-detail-panel.png)
```

## Example User Workflows

### Workflow 1: Weekly Market Check

1. Fetch jobs with `python` search term.
2. Filter by role family `backend` and seniority `senior`.
3. Review top skills and top companies.
4. Export filtered CSV.

### Workflow 2: Salary Transparency Scan

1. Fetch latest jobs.
2. Set salary filter to `Yes`.
3. Compare categories and locations where salary is most frequently disclosed.

### Workflow 3: Trend Monitoring

1. Fetch jobs daily or weekly.
2. Let snapshots accumulate in `data/job_snapshots.csv`.
3. Use historical charts to track job count and skill trends over time.

## Limitations

- Enrichment relies on keyword heuristics, not deep NLP parsing.
- Remote scope inference is text-based and may misclassify ambiguous location strings.
- Salary is tracked as present/absent, not normalized compensation bands.
- Historical insights depend on consistent snapshot cadence.
- Source API schema changes may require mapper updates.

## Future Roadmap

- Add regex-safe keyword filtering and phrase-level matching
- Add salary parsing to numeric ranges (min, max, currency)
- Add date-range filters for publication and fetch date
- Add deployment configuration for Streamlit Community Cloud
- Add CI workflow for automated tests
- Add richer trend analytics (growth rates, moving averages)

## Notes

Legacy learning scripts and historical sandbox outputs were moved to `archive/sandbox/` to keep the root project clean while preserving project history.
