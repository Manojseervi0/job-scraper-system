import re
from datetime import datetime, timezone
from typing import Optional


def clean_text(value: Optional[str]) -> str:
    # text clean
    if not value:
        return ""
    collapsed = re.sub(r"\s+", " ", value)
    return collapsed.strip()


def safe_get(value: Optional[str], default: str = "Not specified") -> str:
    # safe value
    cleaned = clean_text(value)
    return cleaned if cleaned else default


def normalize_salary(value: Optional[str]) -> str:
    # salary clean
    cleaned = clean_text(value)
    return cleaned if cleaned else "Not disclosed"


def utc_now_iso() -> str:
    # UTC time
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def unix_timestamp_to_iso(timestamp: Optional[int]) -> str:
    # unix convert
    if timestamp is None:
        return "Unknown"
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat(
            timespec="seconds"
        )
    except (ValueError, OSError, TypeError):
        return "Unknown"


def truncate(value: str, max_length: int = 500) -> str:
    # text limit
    if len(value) <= max_length:
        return value
    return value[:max_length].rstrip() + "..."