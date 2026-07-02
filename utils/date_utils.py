"""Date parsing helpers."""

from datetime import datetime
from typing import Optional


def parse_deadline(value: Optional[str]) -> Optional[datetime]:
    """Parse HTML date input into a datetime."""
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError:
        return None
