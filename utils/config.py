from pathlib import Path

# project paths

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

DATABASE_PATH = DATA_DIR / "jobs.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
CSV_EXPORT_PATH = EXPORTS_DIR / "jobs.csv"

# HTTP settings

REQUEST_TIMEOUT = 10  # request time

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/json,application/xhtml+xml",
}

# retry count
MAX_RETRIES = 3

# retry delay
RETRY_DELAY = 2

# scraper URLs

PYTHON_ORG_JOBS_URL = "https://www.python.org/jobs/"

REMOTEOK_API_URL = "https://remoteok.com/api"

# company list
GREENHOUSE_COMPANIES = [
    "stripe",
    "figma",
    "airbnb",
]

# URL format
GREENHOUSE_JOBS_URL_TEMPLATE = (
    "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
)

# source names

SOURCE_PYTHON_ORG = "Python.org"
SOURCE_GREENHOUSE = "Greenhouse"
SOURCE_REMOTEOK = "RemoteOK"