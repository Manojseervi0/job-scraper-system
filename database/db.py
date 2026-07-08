import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List

from utils.config import DATABASE_PATH, SCHEMA_PATH
from utils.helpers import utc_now_iso
from utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection(db_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    # DB connection
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()

    except sqlite3.IntegrityError:
        # duplicate rollback
        connection.rollback()
        raise


    except Exception as exc:
        # error rollback
        connection.rollback()
        logger.error(
            "Transaction rolled back due to an unexpected error: %s",
            exc,
        )
        raise

    finally:
        # DB close
        connection.close()


def create_database(db_path: Path = DATABASE_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    # DB ready
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    # schema read
    schema_sql = schema_path.read_text(encoding="utf-8")

    with get_connection(db_path) as connection:
        connection.executescript(schema_sql)

    logger.info("Database created/verified at: %s", db_path)


def insert_job(job: Dict[str, Any], db_path: Path = DATABASE_PATH) -> bool:
    # insert query
    insert_sql = """
        INSERT INTO jobs (
            title, company, location, salary, job_type,
            description, job_url, source, posted_date, scraped_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # values banao
    values = (
        job["title"],
        job["company"],
        job["location"],
        job["salary"],
        job["job_type"],
        job["description"],
        job["job_url"],
        job["source"],
        job["posted_date"],
        utc_now_iso(),
    )

    try:
        with get_connection(db_path) as connection:
            connection.execute(insert_sql, values)
        logger.debug("Inserted job: %s (%s)", job["title"], job["job_url"])
        return True
    except sqlite3.IntegrityError:
        # duplicate skip
        logger.info("Duplicate skipped: %s (%s)", job["title"], job["job_url"])
        return False


def job_exists(job_url: str, db_path: Path = DATABASE_PATH) -> bool:
    # check query
    query = "SELECT 1 FROM jobs WHERE job_url = ? LIMIT 1"

    with get_connection(db_path) as connection:
        cursor = connection.execute(query, (job_url,))
        return cursor.fetchone() is not None


def fetch_all_jobs(db_path: Path = DATABASE_PATH) -> List[Dict[str, Any]]:
    # fetch query
    query = "SELECT * FROM jobs ORDER BY scraped_at DESC"

    with get_connection(db_path) as connection:
        cursor = connection.execute(query)
        rows = cursor.fetchall()

    # dict convert
    jobs = [dict(row) for row in rows]
    logger.info("Fetched %d jobs from database.", len(jobs))
    return jobs


def count_jobs(db_path: Path = DATABASE_PATH) -> int:
    # total count
    query = "SELECT COUNT(*) AS total FROM jobs"

    with get_connection(db_path) as connection:
        cursor = connection.execute(query)
        row = cursor.fetchone()

    return row["total"] if row else 0