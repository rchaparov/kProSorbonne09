"""Shared analytics query helpers."""

from datetime import datetime, timedelta

from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session as DbSession

from database import Note


def _sparkline_notes(
    db: DbSession, now: datetime, project_id: int | None = None
) -> tuple[list[dict], int]:
    """Return daily note counts for the last 14 days (team-wide or per project)."""
    day_start_base = now.replace(hour=0, minute=0, second=0, microsecond=0)
    range_start = day_start_base - timedelta(days=13)

    query = db.query(
        cast(Note.created_at, Date).label("day"),
        func.count(Note.id).label("cnt"),
    ).filter(Note.created_at >= range_start)

    if project_id is not None:
        query = query.filter(Note.project_id == project_id)

    rows = dict(query.group_by(cast(Note.created_at, Date)).all())

    sparkline_data = []
    for i in range(13, -1, -1):
        day = (day_start_base - timedelta(days=i)).date()
        sparkline_data.append(
            {
                "date": day_start_base - timedelta(days=i),
                "count": rows.get(day, 0),
            }
        )

    sparkline_max = max((d["count"] for d in sparkline_data), default=1) or 1
    return sparkline_data, sparkline_max
