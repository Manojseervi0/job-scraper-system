from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from utils.config import CSV_EXPORT_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

# CSV order fix
CSV_COLUMNS = [
    "id",
    "title",
    "company",
    "location",
    "salary",
    "job_type",
    "description",
    "job_url",
    "source",
    "posted_date",
    "scraped_at",
]


def export_jobs_to_csv(
    jobs: List[Dict[str, Any]], export_path: Path = CSV_EXPORT_PATH
) -> bool:
    # data check
    if not jobs:
        logger.warning("No jobs to export — skipping CSV export.")
        return False

    try:
        # folder banao
        export_path.parent.mkdir(parents=True, exist_ok=True)

        # DataFrame banao
        dataframe = pd.DataFrame(jobs)

        # missing column
        for column in CSV_COLUMNS:
            if column not in dataframe.columns:
                dataframe[column] = ""

        # order set
        dataframe = dataframe[CSV_COLUMNS]

        # CSV save
        dataframe.to_csv(export_path, index=False, encoding="utf-8")

        logger.info(
            "CSV exported successfully: %s (%d rows).", export_path, len(dataframe)
        )
        return True

    except Exception as exc:  # export error
        logger.error("CSV export failed: %s", exc)
        return False