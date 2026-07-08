from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.python_org_scraper import PythonOrgScraper
from scrapers.remoteok_scraper import RemoteOKScraper


# sample HTML
PYTHON_ORG_SAMPLE_HTML = """
<html><body>
<ol class="list-recent-jobs">
  <li class="list-recent-jobs__list-item">
    <h2><a href="/jobs/1234/">Senior Python Developer</a></h2>
    <p>Acme Corp, Bengaluru, India</p>
    <time datetime="2026-06-30">June 30, 2026</time>
  </li>
  <li class="list-recent-jobs__list-item">
    <h2><a href="https://external.com/jobs/5678/">Backend Engineer</a></h2>
    <p>RemoteCo</p>
  </li>
  <li class="list-recent-jobs__list-item">
    <h2><a href=""></a></h2>
  </li>
</ol>
</body></html>
"""


def test_python_org_scraper_parses_valid_jobs() -> None:
    # parse test
    scraper = PythonOrgScraper()
    jobs = scraper._parse_jobs(PYTHON_ORG_SAMPLE_HTML)

    assert len(jobs) == 2
    assert jobs[0]["title"] == "Senior Python Developer"
    assert jobs[0]["company"] == "Acme Corp"
    assert jobs[0]["location"] == "Bengaluru, India"
    assert jobs[0]["job_url"] == "https://www.python.org/jobs/1234/"
    assert jobs[0]["posted_date"] == "2026-06-30"


def test_python_org_scraper_handles_missing_fields() -> None:
    # missing test
    scraper = PythonOrgScraper()
    jobs = scraper._parse_jobs(PYTHON_ORG_SAMPLE_HTML)

    second_job = jobs[1]
    assert second_job["title"] == "Backend Engineer"
    assert second_job["location"] == "Not specified"
    assert second_job["posted_date"] == "Unknown"


def test_python_org_scraper_skips_malformed_listing() -> None:
    # skip check
    scraper = PythonOrgScraper()
    jobs = scraper._parse_jobs(PYTHON_ORG_SAMPLE_HTML)

    urls = [job["job_url"] for job in jobs]
    assert "" not in urls


def test_greenhouse_scraper_parses_valid_jobs() -> None:
    # sample payload
    payload = {
        "jobs": [
            {
                "title": "Software Engineer, Backend",
                "absolute_url": "https://boards.greenhouse.io/stripe/jobs/1111",
                "location": {"name": "Remote - India"},
                "content": "<p>We are looking for a <b>backend engineer</b>.</p><p>5+ years experience.</p>",
                "updated_at": "2026-06-15T10:00:00Z",
            }
        ]
    }

    scraper = GreenhouseScraper(companies=["stripe"])
    jobs = scraper._parse_jobs(payload, "stripe")

    assert len(jobs) == 1
    job = jobs[0]
    assert job["title"] == "Software Engineer, Backend"
    assert job["company"] == "Stripe"
    assert job["location"] == "Remote - India"
    assert "<p>" not in job["description"]
    assert "backend engineer" in job["description"]
    assert job["posted_date"] == "2026-06-15T10:00:00Z"


def test_greenhouse_scraper_handles_missing_fields() -> None:
    # missing test
    payload = {
        "jobs": [
            {
                "title": "Product Designer",
                "absolute_url": "https://boards.greenhouse.io/stripe/jobs/2222",
                "location": {},
                "content": None,
                "updated_at": None,
            }
        ]
    }

    scraper = GreenhouseScraper(companies=["stripe"])
    jobs = scraper._parse_jobs(payload, "stripe")

    assert len(jobs) == 1
    assert jobs[0]["location"] == "Not specified"
    assert jobs[0]["posted_date"] == "Unknown"


def test_greenhouse_scraper_skips_entry_without_title() -> None:
    # skip check
    payload = {
        "jobs": [
            {"title": "", "absolute_url": "https://boards.greenhouse.io/stripe/jobs/3333"}
        ]
    }

    scraper = GreenhouseScraper(companies=["stripe"])
    jobs = scraper._parse_jobs(payload, "stripe")

    assert jobs == []


def test_remoteok_scraper_skips_metadata_row_and_parses_jobs() -> None:
    # sample payload
    payload = [
        {"legal": "RemoteOK API legal notice...", "api": True},
        {
            "position": "Senior Backend Engineer",
            "company": "Acme Remote Inc",
            "url": "https://remoteok.com/remote-jobs/12345",
            "location": "Worldwide",
            "salary_min": 90000,
            "salary_max": 130000,
            "tags": ["python", "backend", "senior", "django"],
            "description": "We build remote-first developer tools.",
            "epoch": 1751500000,
        },
    ]

    scraper = RemoteOKScraper()
    jobs = scraper._parse_jobs(payload)

    assert len(jobs) == 1
    job = jobs[0]
    assert job["title"] == "Senior Backend Engineer"
    assert job["salary"] == "$90,000 - $130,000"
    assert job["job_type"] == "python, backend, senior"


def test_remoteok_scraper_handles_missing_salary_and_tags() -> None:
    # missing test
    payload = [
        {"legal": "notice"},
        {
            "position": "Junior Frontend Dev",
            "company": "StartupX",
            "url": "https://remoteok.com/remote-jobs/99999",
            "salary_min": None,
            "salary_max": None,
            "tags": [],
            "description": "",
        },
    ]

    scraper = RemoteOKScraper()
    jobs = scraper._parse_jobs(payload)

    assert len(jobs) == 1
    assert jobs[0]["location"] == "Remote"
    assert jobs[0]["salary"] == "Not disclosed"
    assert jobs[0]["job_type"] == "Not specified"
    assert "StartupX" in jobs[0]["description"]


def test_remoteok_scraper_skips_entry_without_position_or_url() -> None:
    # skip check
    payload = [
        {"legal": "notice"},
        {"position": "", "url": "https://remoteok.com/remote-jobs/00000"},
    ]

    scraper = RemoteOKScraper()
    jobs = scraper._parse_jobs(payload)

    assert jobs == []