import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://remotive.com/api/remote-jobs"
SEARCH_TERM = "python"


def fetch_jobs(search_term="python"):
    params = {"search": search_term}
    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data.get("jobs", [])


def clean_jobs(jobs):
    rows = []

    for job in jobs:
        rows.append(
            {
                "title": job.get("title"),
                "company": job.get("company_name"),
                "category": job.get("category"),
                "job_type": job.get("job_type"),
                "publication_date": job.get("publication_date"),
                "candidate_required_location": job.get("candidate_required_location"),
                "salary": job.get("salary"),
                "url": job.get("url"),
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["title"] = df["title"].fillna("").str.strip()
    df["company"] = df["company"].fillna("").str.strip()
    df["category"] = df["category"].fillna("Unknown").str.strip()
    df["job_type"] = df["job_type"].fillna("Unknown").str.strip()
    df["candidate_required_location"] = (
        df["candidate_required_location"].fillna("Unknown").str.strip()
    )
    df["salary"] = df["salary"].fillna("").astype(str).str.strip()

    df["has_salary"] = df["salary"].apply(lambda x: "Yes" if x else "No")

    return df


def analyze_and_save(df):
    if df.empty:
        print("No jobs found.")
        return

    df.to_csv("remote_jobs.csv", index=False)
    print(f"Saved {len(df)} jobs to remote_jobs.csv")

    print("\nFirst 5 rows:")
    print(df.head())

    top_categories = df["category"].value_counts().head(10)
    print("\nTop categories:")
    print(top_categories)

    top_locations = df["candidate_required_location"].value_counts().head(10)
    print("\nTop candidate locations:")
    print(top_locations)

    top_companies = df["company"].value_counts().head(10)
    print("\nTop companies:")
    print(top_companies)

    salary_counts = df["has_salary"].value_counts()
    print("\nJobs with salary info:")
    print(salary_counts)

    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Total jobs: {len(df)}\n\n")
        f.write("Top Categories:\n")
        f.write(top_categories.to_string())
        f.write("\n\nTop Locations:\n")
        f.write(top_locations.to_string())
        f.write("\n\nTop Companies:\n")
        f.write(top_companies.to_string())
        f.write("\n\nJobs With Salary Info:\n")
        f.write(salary_counts.to_string())

    plt.figure(figsize=(10, 6))
    top_categories.plot(kind="bar")
    plt.title("Top Job Categories")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("categories_chart.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    top_locations.plot(kind="bar")
    plt.title("Top Candidate Locations")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("locations_chart.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    top_companies.plot(kind="bar")
    plt.title("Top Companies Hiring for Search Term")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("companies_chart.png")
    plt.close()

    plt.figure(figsize=(6, 4))
    salary_counts.plot(kind="bar")
    plt.title("Jobs With Salary Info")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("salary_chart.png")
    plt.close()

    print("\nGenerated files:")
    print("- remote_jobs.csv")
    print("- summary.txt")
    print("- categories_chart.png")
    print("- locations_chart.png")
    print("- companies_chart.png")
    print("- salary_chart.png")


def main():
    jobs = fetch_jobs(SEARCH_TERM)
    print(f"Fetched {len(jobs)} jobs from API for search term: {SEARCH_TERM}")

    df = clean_jobs(jobs)

    if not df.empty:
        keywords = [
            "python",
            "developer",
            "engineer",
            "backend",
            "software",
            "automation",
            "api",
        ]
        pattern = "|".join(keywords)
        df = df[df["title"].str.lower().str.contains(pattern, na=False)]
        print(f"Jobs remaining after title filter: {len(df)}")

    analyze_and_save(df)


if __name__ == "__main__":
    main()
