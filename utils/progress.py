"""Project progress calculation utilities."""

from __future__ import annotations

PROJECT_STATUS_LABELS = {
    "planning": "Планирование",
    "active": "В работе",
    "review": "На проверке",
    "on_hold": "Приостановлен",
    "completed": "Завершён",
}

PROJECT_STATUS_COLORS = {
    "planning": "bg-gray-100 text-gray-700",
    "active": "bg-indigo-50 text-indigo-700",
    "review": "bg-amber-50 text-amber-700",
    "on_hold": "bg-orange-50 text-orange-700",
    "completed": "bg-green-50 text-green-700",
}

PROJECT_STATUS_BASE_PROGRESS = {
    "planning": 0,
    "active": 20,
    "review": 60,
    "on_hold": 20,
    "completed": 100,
}

PROJECT_STATUSES = list(PROJECT_STATUS_LABELS.keys())


def project_progress(
    status: str, checklist_done: int, checklist_total: int
) -> int:
    """Compute overall project progress percentage (0-100)."""
    if status == "completed":
        return 100
    if checklist_total > 0:
        return round(checklist_done / checklist_total * 100)
    return PROJECT_STATUS_BASE_PROGRESS.get(status, 0)
