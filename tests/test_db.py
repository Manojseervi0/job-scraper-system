from pathlib import Path

import pytest

from database import db


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    # temp DB
    db_path = tmp_path / "test_jobs.db"
    db.create_database(db_path=db_path)
    return db_path


@pytest.fixture
def sample_job() -> dict:
    # sample job
    return {
        "title": "Python Developer",
        "company": "Acme Corp",
        "location": "Remote",
        "salary": "Not disclosed",
        "job_type": "Full-time",
        "description": "Build cool things with Python.",
        "job_url": "https://example.com/jobs/1",
        "source": "Test",
        "posted_date": "2026-01-01",
    }


def test_create_database_creates_file(temp_db: Path) -> None:
    # file check
    assert temp_db.exists()


def test_insert_new_job_succeeds(temp_db: Path, sample_job: dict) -> None:
    # insert test
    result = db.insert_job(sample_job, db_path=temp_db)
    assert result is True
    assert db.count_jobs(db_path=temp_db) == 1


def test_insert_duplicate_job_is_skipped(temp_db: Path, sample_job: dict) -> None:
    # duplicate test
    db.insert_job(sample_job, db_path=temp_db)

    duplicate = dict(sample_job)
    duplicate["title"] = "A Different Title, Same URL"

    result = db.insert_job(duplicate, db_path=temp_db)

    assert result is False
    assert db.count_jobs(db_path=temp_db) == 1


def test_job_exists(temp_db: Path, sample_job: dict) -> None:
    # exists check
    assert db.job_exists(sample_job["job_url"], db_path=temp_db) is False
    db.insert_job(sample_job, db_path=temp_db)
    assert db.job_exists(sample_job["job_url"], db_path=temp_db) is True


def test_fetch_all_jobs_returns_inserted_jobs(temp_db: Path, sample_job: dict) -> None:
    # fetch test
    db.insert_job(sample_job, db_path=temp_db)

    second_job = dict(sample_job)
    second_job["job_url"] = "https://example.com/jobs/2"
    second_job["title"] = "Backend Engineer"
    db.insert_job(second_job, db_path=temp_db)

    all_jobs = db.fetch_all_jobs(db_path=temp_db)

    assert len(all_jobs) == 2
    titles = {job["title"] for job in all_jobs}
    assert titles == {"Python Developer", "Backend Engineer"}
    assert all(job["scraped_at"] for job in all_jobs)


def test_insert_job_missing_field_raises_and_does_not_corrupt_db(
    temp_db: Path, sample_job: dict
) -> None:
    # error test
    db.insert_job(sample_job, db_path=temp_db)

    broken_job = dict(sample_job)
    broken_job["job_url"] = "https://example.com/jobs/broken"
    del broken_job["title"]

    with pytest.raises(KeyError):
        db.insert_job(broken_job, db_path=temp_db)

    # DB safe
    assert db.count_jobs(db_path=temp_db) == 1