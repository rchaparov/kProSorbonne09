"""Pagination helpers for page number lists."""

from __future__ import annotations


def paginate_range(current: int, total: int, window: int = 1) -> list:
    """Build a compact page number list with '...' separators.

    Example: paginate_range(5, 10) -> [1, '...', 4, 5, 6, '...', 10]
    """
    if total <= 1:
        return [1] if total == 1 else []

    pages = {1, total, current}
    for offset in range(1, window + 1):
        pages.add(current - offset)
        pages.add(current + offset)
    pages = sorted(p for p in pages if 1 <= p <= total)

    result = []
    prev = None
    for p in pages:
        if prev is not None and p - prev > 1:
            result.append("...")
        result.append(p)
        prev = p
    return result
