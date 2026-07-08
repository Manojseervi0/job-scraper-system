from typing import Any, Dict, List, Tuple

from database.db import create_database, fetch_all_jobs, insert_job
from exporter.csv_exporter import export_jobs_to_csv
from scrapers.base_scraper import BaseScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.python_org_scraper import PythonOrgScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from utils.logger import get_logger

logger = get_logger(__name__)


def get_scrapers() -> List[BaseScraper]:
    # scraper list
    return [
        PythonOrgScraper(),
        GreenhouseScraper(),
        RemoteOKScraper(),
    ]


def run_scrapers(scrapers: List[BaseScraper]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    # result store
    all_jobs: List[Dict[str, Any]] = []
    per_source_counts: Dict[str, int] = {}

    # scraper loop
    for scraper in scrapers:
        try:
            jobs = scraper.scrape()
        except Exception as exc:  # scraper fail
            logger.error(
                "[%s] Scraper crashed unexpectedly, skipping it: %s",
                scraper.source_name,
                exc,
            )
            jobs = []

        per_source_counts[scraper.source_name] = len(jobs)
        all_jobs.extend(jobs)

    return all_jobs, per_source_counts


def store_jobs(jobs: List[Dict[str, Any]]) -> Tuple[int, int]:
    # counter start
    inserted_count = 0
    skipped_count = 0

    # job loop
    for job in jobs:
        was_inserted = insert_job(job)

        if was_inserted:
            inserted_count += 1
        else:
            skipped_count += 1

    return inserted_count, skipped_count


def print_summary(
    per_source_counts: Dict[str, int],
    inserted_count: int,
    skipped_count: int,
    csv_success: bool,
) -> None:
    # summary print
    print("\n" + "=" * 40)
    print("JOB SCRAPER SYSTEM — RUN SUMMARY")
    print("=" * 40)

    # source stats
    for source_name, count in per_source_counts.items():
        print(f"{source_name:<15}: {count} jobs")

    print("-" * 40)
    print(f"{'Inserted':<15}: {inserted_count}")
    print(f"{'Skipped':<15}: {skipped_count}")
    print("-" * 40)

    # export status
    if csv_success:
        print("CSV exported successfully.")
    else:
        print("CSV export failed or there was no data to export.")

    print("=" * 40 + "\n")


def main() -> None:
    # run start
    logger.info("Starting Job Scraper System run.")

    # DB ready
    create_database()

    # scraper run
    scrapers = get_scrapers()
    all_jobs, per_source_counts = run_scrapers(scrapers)

    logger.info("Collected %d jobs total across all sources.", len(all_jobs))

    # DB save
    inserted_count, skipped_count = store_jobs(all_jobs)
    logger.info(
        "Storage complete: %d inserted, %d skipped as duplicates.",
        inserted_count,
        skipped_count,
    )

    # CSV export
    all_stored_jobs = fetch_all_jobs()
    csv_success = export_jobs_to_csv(all_stored_jobs)

    # final summary
    print_summary(per_source_counts, inserted_count, skipped_count, csv_success)

    # run end
    logger.info("Job Scraper System run complete.")


if __name__ == "__main__":
    main()