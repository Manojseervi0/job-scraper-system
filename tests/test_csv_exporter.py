from pathlib import Path

import pandas as pd
import pytest

from exporter.csv_exporter import export_jobs_to_csv


@pytest.fixture
def sample_jobs() -> list:
    # sample data
    return [
        {
            "id": 1,
            "title": "Python Dev",
            "company": "Acme, Inc.",
            "location": "Remote",
            "salary": "100k",
            "job_type": "Full-time",
            "description": 'Great role, with "quotes" and,\ncommas and newlines.',
            "job_url": "https://example.com/1",
            "source": "Test",
            "posted_date": "2026-01-01",
            "scraped_at": "2026-01-02T00:00:00",
        },
        {
            "id": 2,
            "title": "Backend Engineer",
            "company": "Beta",
            "location": "NYC",
            "salary": "Not disclosed",
            "job_type": "Contract",
            "description": "Simple description.",
            "job_url": "https://example.com/2",
            "source": "Test",
            "posted_date": "2026-01-03",
            "scraped_at": "2026-01-04T00:00:00",
        },
    ]


def test_export_returns_true_on_success(tmp_path: Path, sample_jobs: list) -> None:
    # export test
    export_path = tmp_path / "jobs.csv"
    result = export_jobs_to_csv(sample_jobs, export_path=export_path)

    assert result is True
    assert export_path.exists()


def test_exported_csv_preserves_special_characters(
    tmp_path: Path, sample_jobs: list
) -> None:
    # special chars
    export_path = tmp_path / "jobs.csv"
    export_jobs_to_csv(sample_jobs, export_path=export_path)

    df = pd.read_csv(export_path)

    assert len(df) == 2
    assert df.iloc[0]["company"] == "Acme, Inc."
    assert "quotes" in df.iloc[0]["description"]


def test_exported_csv_has_expected_columns(tmp_path: Path, sample_jobs: list) -> None:
    # column check
    export_path = tmp_path / "jobs.csv"
    export_jobs_to_csv(sample_jobs, export_path=export_path)

    df = pd.read_csv(export_path)
    expected_columns = [
        "id", "title", "company", "location", "salary", "job_type",
        "description", "job_url", "source", "posted_date", "scraped_at",
    ]
    assert list(df.columns) == expected_columns


def test_export_empty_list_returns_false(tmp_path: Path) -> None:
    # empty check
    export_path = tmp_path / "jobs.csv"
    result = export_jobs_to_csv([], export_path=export_path)

    assert result is False
    assert not export_path.exists()