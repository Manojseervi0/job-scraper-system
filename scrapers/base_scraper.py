import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException

from utils.config import (
    DEFAULT_HEADERS,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
)
from utils.helpers import clean_text
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseScraper(ABC):

    def __init__(self, source_name: str) -> None:
        # source setup
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        # child implement
        raise NotImplementedError

    def fetch_page(self, url: str) -> Optional[str]:
        # HTML fetch
        return self._request_with_retries(url, expect_json=False)

    def fetch_json(self, url: str) -> Optional[Any]:
        # JSON fetch
        return self._request_with_retries(url, expect_json=True)

    def _request_with_retries(
        self, url: str, expect_json: bool
    ) -> Optional[Any]:
        # retry logic
        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    "[%s] Fetching page (attempt %d/%d): %s",
                    self.source_name,
                    attempt,
                    MAX_RETRIES,
                    url,
                )
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                # JSON return
                if expect_json:
                    return response.json()

                # HTML return
                return response.text

            except RequestException as exc:
                last_error = exc
                logger.warning(
                    "[%s] Request failed (attempt %d/%d): %s",
                    self.source_name,
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    # retry wait
                    time.sleep(RETRY_DELAY)

            except ValueError as exc:
                # JSON error
                last_error = exc
                logger.warning(
                    "[%s] Invalid JSON response (attempt %d/%d): %s",
                    self.source_name,
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    # retry wait
                    time.sleep(RETRY_DELAY)

        # final fail
        logger.error(
            "[%s] Failed to fetch %s after %d attempts. Last error: %s",
            self.source_name,
            url,
            MAX_RETRIES,
            last_error,
        )
        return None

    @staticmethod
    def clean_text(value: Optional[str]) -> str:
        # text clean
        return clean_text(value)

    @staticmethod
    def make_absolute_url(base_url: str, possibly_relative_url: str) -> str:
        # full URL banao
        if not possibly_relative_url:
            return ""
        return urljoin(base_url, possibly_relative_url)

    def build_job(
        self,
        title: str,
        company: str,
        location: str,
        salary: str,
        job_type: str,
        description: str,
        job_url: str,
        posted_date: str,
    ) -> Dict[str, Any]:
        # job dict
        return {
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "job_type": job_type,
            "description": description,
            "job_url": job_url,
            "source": self.source_name,
            "posted_date": posted_date,
        }