"""Dashboard routes."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_current_user, get_unread_count
from database import ChecklistItem, Note, Project, ProjectMember, get_db_session
from main import templates
from utils.nav import nav_context
from utils.progress import (
    PROJECT_STATUSES,
    PROJECT_STATUS_COLORS,
    PROJECT_STATUS_LABELS,
    project_progress,
)

router = APIRouter(tags=["dashboard"])


def progress_bar_color(status: str, deadline, now: datetime) -> str:
    """Return progress bar color based on project status and deadline."""
    if status == "completed":
        return "#639922"
    if deadline and deadline < now:
        return "#A32D2D"
    return "#378ADD"


@router.get("/")
async def dashboard(
    request: Request,
    status: Optional[str] = None,
    mine: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the project list for all authenticated users."""
    query = db.query(Project).order_by(Project.created_at.desc())

    active_status = status if status in PROJECT_STATUSES else None
    if active_status:
        query = query.filter_by(status=active_status)

    mine_only = bool(mine)
    if mine_only:
        member_project_ids = {
            row[0]
            for row in db.query(ProjectMember.project_id)
            .filter_by(user_id=current_user.id)
            .all()
        }
        if member_project_ids:
            query = query.filter(Project.id.in_(member_project_ids))
        else:
            query = query.filter(Project.id.in_([]))

    projects = query.all()
    project_ids = [project.id for project in projects]
    now = datetime.utcnow()

    member_counts = dict(
        db.query(ProjectMember.project_id, func.count(ProjectMember.id))
        .group_by(ProjectMember.project_id)
        .all()
    )

    checklist_stats = {}
    rows = (
        db.query(
            ChecklistItem.project_id,
            func.count(ChecklistItem.id).label("total"),
            func.sum(func.cast(ChecklistItem.is_done, Integer)).label("done"),
        )
        .group_by(ChecklistItem.project_id)
        .all()
    )
    for row in rows:
        checklist_stats[row.project_id] = {
            "total": row.total or 0,
            "done": int(row.done or 0),
        }

    last_notes: dict[int, datetime] = {}
    if project_ids:
        last_note_subq = (
            db.query(
                Note.project_id,
                func.max(Note.created_at).label("last_note_at"),
            )
            .filter(Note.project_id.in_(project_ids))
            .group_by(Note.project_id)
            .subquery()
        )
        last_notes = dict(
            db.query(last_note_subq.c.project_id, last_note_subq.c.last_note_at).all()
        )

    members_per_project: dict[int, list] = {}
    if project_ids:
        all_members = (
            db.query(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .filter(ProjectMember.project_id.in_(project_ids))
            .order_by(ProjectMember.joined_at.asc())
            .all()
        )
        for member in all_members:
            if member.user:
                members_per_project.setdefault(member.project_id, []).append(member.user)

    progress_pcts = {}
    progress_colors = {}
    for project in projects:
        stats = checklist_stats.get(project.id, {"done": 0, "total": 0})
        progress_pcts[project.id] = project_progress(
            project.status, stats["done"], stats["total"]
        )
        progress_colors[project.id] = progress_bar_color(
            project.status, project.deadline, now
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "projects": projects,
            "member_counts": member_counts,
            "checklist_stats": checklist_stats,
            "progress_pcts": progress_pcts,
            "progress_colors": progress_colors,
            "last_notes": last_notes,
            "members_per_project": members_per_project,
            "activity_threshold": now - timedelta(hours=24),
            "status_labels": PROJECT_STATUS_LABELS,
            "status_colors": PROJECT_STATUS_COLORS,
            "active_status": active_status,
            "mine_only": mine_only,
            "all_statuses": PROJECT_STATUSES,
            "now": now,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )
