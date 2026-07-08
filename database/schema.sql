-- Schema for the Job Scraper System's SQLite database.
--
-- A single `jobs` table stores every job pulled from every scraper.
-- `job_url` is UNIQUE, which is the primary mechanism used to detect
-- and skip duplicate jobs across repeated scraper runs.

CREATE TABLE IF NOT EXISTS jobs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    company       TEXT NOT NULL,
    location      TEXT NOT NULL,
    salary        TEXT NOT NULL,
    job_type      TEXT NOT NULL,
    description   TEXT NOT NULL,
    job_url       TEXT NOT NULL UNIQUE,
    source        TEXT NOT NULL,
    posted_date   TEXT NOT NULL,
    scraped_at    TEXT NOT NULL
);

-- Speeds up lookups/filters by source (e.g. "show me all Greenhouse jobs")
-- and by scraped_at (e.g. "show me jobs scraped today").
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs (source);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs (scraped_at);
