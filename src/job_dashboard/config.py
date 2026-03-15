"""Centralized project configuration."""

API_URL = "https://remotive.com/api/remote-jobs"
DEFAULT_SEARCH_TERM = ""
DEFAULT_TITLE_KEYWORDS = ""
DEFAULT_EXCLUDE_KEYWORDS = ""
SKILL_KEYWORDS = [
    "python",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "react",
    "javascript",
    "typescript",
    "java",
    "git",
    "api",
    "databricks",
    "pandas",
    "flask",
    "django",
    "spark",
    "airflow",
    "terraform",
    "ansible",
    "gcp",
    "azure",
    "node",
    "fastapi",
    "postgres",
    "mongodb",
    "linux",
    "go",
    "rust",
    "c#",
    "php",
]

SENIORITY_KEYWORDS = {
    "intern": ["intern", "internship", "trainee"],
    "junior": ["junior", "jr", "entry level", "associate"],
    "mid": ["mid", "mid-level", "intermediate"],
    "senior": ["senior", "sr", "expert"],
    "staff": ["staff"],
    "lead": ["lead", "team lead", "tech lead"],
    "principal": ["principal", "architect"],
}

ROLE_FAMILY_KEYWORDS = {
    "backend": ["backend", "back-end", "api", "server", "python", "java", "golang"],
    "frontend": ["frontend", "front-end", "react", "vue", "angular", "ui engineer"],
    "fullstack": ["fullstack", "full-stack"],
    "data": ["data", "machine learning", "ml", "ai", "analytics", "bi", "scientist"],
    "devops": [
        "devops",
        "sre",
        "platform",
        "infrastructure",
        "cloud",
        "kubernetes",
        "terraform",
    ],
    "security": ["security", "infosec", "application security", "soc", "pentest"],
    "qa": ["qa", "quality assurance", "test engineer", "automation tester"],
    "mobile": ["mobile", "android", "ios", "react native", "flutter"],
    "product": ["product manager", "product owner"],
    "design": ["designer", "ux", "ui/ux", "product design"],
    "support": ["support", "customer success", "technical support"],
}

REMOTE_SCOPE_KEYWORDS = {
    "worldwide": ["worldwide", "global", "anywhere", "all countries"],
    "us-only": ["us", "usa", "united states", "us-only", "u.s."],
    "europe-only": ["europe", "eu", "emea", "uk", "europe-only"],
}

SNAPSHOT_CSV_PATH = "data/job_snapshots.csv"
