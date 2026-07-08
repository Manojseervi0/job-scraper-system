import logging
from pathlib import Path

# logs path
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOGS_DIR / "scraper.log"

# log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _ensure_logs_dir() -> None:
    # folder banao
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    # logs ready
    _ensure_logs_dir()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # duplicate check
    if logger.handlers:
        return logger

    # formatter set
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # console log
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # file log
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # double log stop
    logger.propagate = False

    return logger