# Job Dashboard

A lightweight web app for tracking your job applications — built with Python, Flask, and SQLite.

## Features

- Track applications with company, position, status, location, salary, URL, and notes
- Dashboard statistics (total, interviewing, offers, rejections)
- Filter applications by status
- Add, edit, and delete applications
- Responsive, clean UI

## Statuses

`Applied` → `Phone Screen` → `Interview` → `Technical` → `Offer` / `Rejected` / `Withdrawn`

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/LewisMA1224/job_dashboard.git
cd job_dashboard

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open <http://127.0.0.1:5000> in your browser.

## Project Structure

```
job_dashboard/
├── app.py               # Flask application & routes
├── requirements.txt     # Python dependencies
├── static/
│   └── css/
│       └── style.css    # Stylesheet
└── templates/
    ├── base.html        # Shared layout (navbar, flash messages)
    ├── index.html       # Dashboard / job list
    └── form.html        # Add / Edit form
```

## Configuration

| Environment variable | Default            | Description                      |
|----------------------|--------------------|----------------------------------|
| `SECRET_KEY`         | `change-me-in-production` | Flask session secret key |

Set `SECRET_KEY` to a long random string before deploying.
