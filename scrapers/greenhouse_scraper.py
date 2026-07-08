import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.config import GREENHOUSE_COMPANIES, GREENHOUSE_JOBS_URL_TEMPLATE, SOURCE_GREENHOUSE
from utils.helpers import safe_get, truncate
from utils.logger import get_logger

logger = get_logger(__name__)


class GreenhouseScraper(BaseScraper):

    def __init__(self, companies: List[str] | None = None) -> None:
        super().__init__(source_name=SOURCE_GREENHOUSE)
        # company list
        self.companies = companies if companies is not None else GREENHOUSE_COMPANIES

    def scrape(self) -> List[Dict[str, Any]]:
        # final jobs
        all_jobs: List[Dict[str, Any]] = []

        # company loop
        for company in self.companies:
            url = GREENHOUSE_JOBS_URL_TEMPLATE.format(company=company)
            payload = self.fetch_json(url)

            if payload is None:
                logger.error(
                    "[%s] No data returned for company '%s', skipping.",
                    self.source_name,
                    company,
                )
                continue

            # jobs parse
            company_jobs = self._parse_jobs(payload, company)
            logger.info(
                "[%s] Found %d jobs for company '%s'.",
                self.source_name,
                len(company_jobs),
                company,
            )
            all_jobs.extend(company_jobs)

        logger.info("[%s] Found %d jobs total.", self.source_name, len(all_jobs))
        return all_jobs

    def _parse_jobs(self, payload: Dict[str, Any], company: str) -> List[Dict[str, Any]]:
        # jobs list
        jobs: List[Dict[str, Any]] = []
        raw_jobs = payload.get("jobs", [])

        # type check
        if not isinstance(raw_jobs, list):
            logger.warning(
                "[%s] Unexpected payload shape for company '%s' — 'jobs' is not a list.",
                self.source_name,
                company,
            )
            return jobs

        # job loop
        for raw_job in raw_jobs:
            try:
                job = self._parse_single_job(raw_job, company)
                if job is not None:
                    jobs.append(job)
            except Exception as exc:  # bad entry
                logger.warning(
                    "[%s] Failed to parse a job entry for company '%s', skipping: %s",
                    self.source_name,
                    company,
                    exc,
                )

        return jobs

    def _parse_single_job(
        self, raw_job: Dict[str, Any], company: str
    ) -> Dict[str, Any] | None:
        # fields read
        title = self.clean_text(raw_job.get("title"))
        job_url = self.clean_text(raw_job.get("absolute_url"))

        # required check
        if not title or not job_url:
            return None

        location_obj = raw_job.get("location") or {}
        location = safe_get(location_obj.get("name"), "Not specified")

        # HTML clean
        raw_content = raw_job.get("content")
        if raw_content:
            extracted = BeautifulSoup(raw_content, "lxml").get_text(separator=" ")
            plain_content = self.clean_text(extracted)

            # space hatao
            plain_content = re.sub(r"\s+([.,;:!?])", r"\1", plain_content)
        else:
            plain_content = ""

        # desc banao
        description = (
            truncate(plain_content, max_length=500)
            if plain_content
            else f"{title} at {company.title()}. See full listing for details."
        )

        # final job
        return self.build_job(
            title=title,
            company=company.title(),
            location=location,
            salary="Not disclosed",
            job_type="Not specified",
            description=description,
            job_url=job_url,
            posted_date=safe_get(raw_job.get("updated_at"), "Unknown"),
        )