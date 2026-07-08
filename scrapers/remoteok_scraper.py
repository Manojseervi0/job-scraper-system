from typing import Any, Dict, List

from scrapers.base_scraper import BaseScraper
from utils.config import REMOTEOK_API_URL, SOURCE_REMOTEOK
from utils.helpers import safe_get, truncate, unix_timestamp_to_iso
from utils.logger import get_logger

logger = get_logger(__name__)


class RemoteOKScraper(BaseScraper):

    def __init__(self) -> None:
        super().__init__(source_name=SOURCE_REMOTEOK)

    def scrape(self) -> List[Dict[str, Any]]:
        # API fetch
        payload = self.fetch_json(REMOTEOK_API_URL)
        if payload is None:
            logger.error("[%s] No data returned, skipping.", self.source_name)
            return []

        # jobs parse
        jobs = self._parse_jobs(payload)
        logger.info("[%s] Found %d jobs.", self.source_name, len(jobs))
        return jobs

    def _parse_jobs(self, payload: Any) -> List[Dict[str, Any]]:
        # jobs list
        jobs: List[Dict[str, Any]] = []

        # type check
        if not isinstance(payload, list):
            logger.warning(
                "[%s] Unexpected payload shape — expected a list.",
                self.source_name,
            )
            return jobs

        # meta skip
        raw_jobs = payload[1:] if len(payload) > 1 else []

        # job loop
        for raw_job in raw_jobs:
            try:
                job = self._parse_single_job(raw_job)
                if job is not None:
                    jobs.append(job)
            except Exception as exc:  # bad entry
                logger.warning(
                    "[%s] Failed to parse a job entry, skipping: %s",
                    self.source_name,
                    exc,
                )

        return jobs

    def _parse_single_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any] | None:
        # dict check
        if not isinstance(raw_job, dict):
            return None

        # fields read
        title = self.clean_text(raw_job.get("position") or raw_job.get("title"))
        job_url = self.clean_text(raw_job.get("url"))

        # required check
        if not title or not job_url:
            return None

        company = safe_get(raw_job.get("company"), "Unknown Company")

        # location set
        location = safe_get(raw_job.get("location"), "Remote")

        salary_min = raw_job.get("salary_min")
        salary_max = raw_job.get("salary_max")
        salary = self._format_salary(salary_min, salary_max)

        # tags join
        tags = raw_job.get("tags")
        job_type = ", ".join(tags[:3]) if isinstance(tags, list) and tags else "Not specified"

        # desc banao
        description = truncate(
            self.clean_text(raw_job.get("description")), max_length=500
        )
        if not description:
            description = f"{title} at {company}. See full listing for details."

        # date read
        posted_date = unix_timestamp_to_iso(raw_job.get("epoch"))
        if posted_date == "Unknown":
            posted_date = safe_get(raw_job.get("date"), "Unknown")

        # final job
        return self.build_job(
            title=title,
            company=company,
            location=location,
            salary=salary,
            job_type=job_type,
            description=description,
            job_url=job_url,
            posted_date=posted_date,
        )

    @staticmethod
    def _format_salary(salary_min: Any, salary_max: Any) -> str:
        # min salary
        try:
            min_val = int(salary_min) if salary_min else None
        except (ValueError, TypeError):
            min_val = None

        # max salary
        try:
            max_val = int(salary_max) if salary_max else None
        except (ValueError, TypeError):
            max_val = None

        # range return
        if min_val and max_val:
            return f"${min_val:,} - ${max_val:,}"
        if min_val:
            return f"${min_val:,}+"
        if max_val:
            return f"Up to ${max_val:,}"
        return "Not disclosed"