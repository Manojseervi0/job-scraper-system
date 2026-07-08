from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.config import PYTHON_ORG_JOBS_URL, SOURCE_PYTHON_ORG
from utils.helpers import safe_get, truncate
from utils.logger import get_logger

logger = get_logger(__name__)


class PythonOrgScraper(BaseScraper):

    def __init__(self) -> None:
        super().__init__(source_name=SOURCE_PYTHON_ORG)

    def scrape(self) -> List[Dict[str, Any]]:
        # page fetch
        html = self.fetch_page(PYTHON_ORG_JOBS_URL)
        if html is None:
            logger.error("[%s] No HTML returned, skipping.", self.source_name)
            return []

        # jobs parse
        jobs = self._parse_jobs(html)
        logger.info("[%s] Found %d jobs.", self.source_name, len(jobs))
        return jobs

    def _parse_jobs(self, html: str) -> List[Dict[str, Any]]:
        # HTML parse
        soup = BeautifulSoup(html, "lxml")
        jobs: List[Dict[str, Any]] = []

        # job cards
        list_items = soup.select("ol.list-recent-jobs >li"
        ""
        "")

        # data check
        if not list_items:
            logger.warning(
                "[%s] No job list items found — page structure may have changed.",
                self.source_name,
            )
            return jobs

        # card loop
        for item in list_items:
            try:
                job = self._parse_single_job(item)
                if job is not None:
                    jobs.append(job)
            except Exception as exc:  # bad listing
                logger.warning(
                    "[%s] Failed to parse a job listing, skipping it: %s",
                    self.source_name,
                    exc,
                )

        return jobs

    def _parse_single_job(self, item: Any) -> Dict[str, Any] | None:
        # title link
        title_link = item.select_one("h2 a")
        if title_link is None:
            return None

        # fields read
        title = self.clean_text(title_link.get_text())
        relative_url = title_link.get("href", "")
        job_url = self.make_absolute_url(PYTHON_ORG_JOBS_URL, relative_url)

        # required check
        if not title or not job_url:
            return None

        # meta split
        meta_paragraph = item.select_one("p")
        company, location = self._split_company_location(meta_paragraph)

        # job type
        job_type_el = item.select_one(".listing-company-name + a, .job-type")
        job_type = safe_get(job_type_el.get_text() if job_type_el else None)

        # desc banao
        description = truncate(
            f"{title} at {safe_get(company, 'Unknown Company')}. "
            f"See full listing for details.",
            max_length=500,
        )

        # final job
        return self.build_job(
            title=title,
            company=safe_get(company, "Unknown Company"),
            location=safe_get(location, "Not specified"),
            salary="Not disclosed",
            job_type=job_type,
            description=description,
            job_url=job_url,
            posted_date=self._extract_posted_date(item),
        )

    def _split_company_location(self, meta_paragraph: Any) -> tuple[str, str]:
        # empty check
        if meta_paragraph is None:
            return "", ""

        text = self.clean_text(meta_paragraph.get_text())
        if not text:
            return "", ""

        # company split
        if "," in text:
            company, location = text.split(",", 1)
            return company.strip(), location.strip()

        # only company
        return text, ""

    def _extract_posted_date(self, item: Any) -> str:
        # date read
        time_el = item.select_one("time")
        if time_el is None:
            return "Unknown"

        # attr first
        datetime_attr = time_el.get("datetime")
        if datetime_attr:
            return self.clean_text(datetime_attr)

        # text fallback
        return safe_get(time_el.get_text(), "Unknown")