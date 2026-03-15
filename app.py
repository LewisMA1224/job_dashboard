from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                company   TEXT    NOT NULL,
                position  TEXT    NOT NULL,
                status    TEXT    NOT NULL DEFAULT 'Applied',
                location  TEXT,
                url       TEXT,
                salary    TEXT,
                notes     TEXT,
                applied_date TEXT NOT NULL
            )
            """
        )
        conn.commit()


STATUSES = ["Applied", "Phone Screen", "Interview", "Technical", "Offer", "Rejected", "Withdrawn"]


@app.route("/")
def index():
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY applied_date DESC").fetchall()

    stats = {
        "total": len(jobs),
        "applied": sum(1 for j in jobs if j["status"] == "Applied"),
        "interview": sum(1 for j in jobs if j["status"] in ("Phone Screen", "Interview", "Technical")),
        "offer": sum(1 for j in jobs if j["status"] == "Offer"),
        "rejected": sum(1 for j in jobs if j["status"] == "Rejected"),
    }

    status_filter = request.args.get("status", "")
    if status_filter:
        jobs = [j for j in jobs if j["status"] == status_filter]

    return render_template("index.html", jobs=jobs, stats=stats, statuses=STATUSES, status_filter=status_filter)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        company = request.form["company"].strip()
        position = request.form["position"].strip()
        status = request.form["status"]
        location = request.form.get("location", "").strip()
        url = request.form.get("url", "").strip()
        salary = request.form.get("salary", "").strip()
        notes = request.form.get("notes", "").strip()
        applied_date = request.form.get("applied_date") or datetime.today().strftime("%Y-%m-%d")

        if not company or not position:
            flash("Company and Position are required.", "error")
            return render_template("form.html", job=request.form, statuses=STATUSES, action="Add")

        with get_db() as conn:
            conn.execute(
                "INSERT INTO jobs (company, position, status, location, url, salary, notes, applied_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (company, position, status, location, url, salary, notes, applied_date),
            )
            conn.commit()
        flash(f"Added {position} at {company}.", "success")
        return redirect(url_for("index"))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template("form.html", job={"status": "Applied", "applied_date": today}, statuses=STATUSES, action="Add")


@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if job is None:
        flash("Job not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        company = request.form["company"].strip()
        position = request.form["position"].strip()
        status = request.form["status"]
        location = request.form.get("location", "").strip()
        url = request.form.get("url", "").strip()
        salary = request.form.get("salary", "").strip()
        notes = request.form.get("notes", "").strip()
        applied_date = request.form.get("applied_date", job["applied_date"])

        if not company or not position:
            flash("Company and Position are required.", "error")
            return render_template("form.html", job=request.form, statuses=STATUSES, action="Edit")

        with get_db() as conn:
            conn.execute(
                "UPDATE jobs SET company=?, position=?, status=?, location=?, url=?, salary=?, notes=?, applied_date=? WHERE id=?",
                (company, position, status, location, url, salary, notes, applied_date, job_id),
            )
            conn.commit()
        flash(f"Updated {position} at {company}.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", job=job, statuses=STATUSES, action="Edit")


@app.route("/delete/<int:job_id>", methods=["POST"])
def delete(job_id):
    with get_db() as conn:
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
    flash("Job application deleted.", "success")
    return redirect(url_for("index"))


with app.app_context():
    init_db()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
