"""Team analytics dashboard routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from auth import get_current_user, get_unread_count
from database import (
    ChecklistItem,
    ChecklistItemAssignee,
    Note,
    Project,
    ProjectMember,
    User,
    get_db_session,
)
from utils.progress import PROJECT_STATUS_LABELS, project_progress

router = APIRouter(tags=["analytics"])
templates = Jinja2Templates(directory="templates")


@router.get("/analytics")
async def analytics_page(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render aggregated team analytics for all authenticated users."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    now = datetime.utcnow()

    status_rows = (
        db.query(Project.status, func.count(Project.id))
        .group_by(Project.status)
        .all()
    )
    status_counts = {status: 0 for status in PROJECT_STATUS_LABELS}
    for status, count in status_rows:
        if status in status_counts:
            status_counts[status] = count
        else:
            status_counts[status] = count
    total_projects = sum(status_counts.values())

    risk_threshold = now + timedelta(days=3)
    risky_projects = (
        db.query(Project)
        .filter(
            Project.status != "completed",
            Project.deadline.isnot(None),
            Project.deadline <= risk_threshold,
        )
        .order_by(Project.deadline.asc())
        .all()
    )

    project_counts = dict(
        db.query(ProjectMember.user_id, func.count(ProjectMember.project_id))
        .group_by(ProjectMember.user_id)
        .all()
    )
    open_task_counts = dict(
        db.query(ChecklistItemAssignee.user_id, func.count(ChecklistItemAssignee.id))
        .join(ChecklistItem, ChecklistItem.id == ChecklistItemAssignee.item_id)
        .filter(ChecklistItem.is_done.is_(False))
        .group_by(ChecklistItemAssignee.user_id)
        .all()
    )
    users = db.query(User).filter_by(is_active=True).all()
    workload = [
        {
            "user": user,
            "project_count": project_counts.get(user.id, 0),
            "open_tasks": open_task_counts.get(user.id, 0),
        }
        for user in users
    ]
    workload.sort(key=lambda row: row["open_tasks"], reverse=True)

    active_projects = [
        project for project in db.query(Project).all() if project.status != "completed"
    ]
    progresses = []
    for project in active_projects:
        total = (
            db.query(func.count(ChecklistItem.id))
            .filter_by(project_id=project.id)
            .scalar()
        ) or 0
        done = (
            db.query(func.count(ChecklistItem.id))
            .filter_by(project_id=project.id, is_done=True)
            .scalar()
        ) or 0
        progresses.append(project_progress(project.status, done, total))
    avg_progress = round(sum(progresses) / len(progresses)) if progresses else 0

    week_ago = now - timedelta(days=7)
    notes_this_week = (
        db.query(func.count(Note.id)).filter(Note.created_at >= week_ago).scalar()
    ) or 0

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "current_user": current_user,
            "status_counts": status_counts,
            "status_labels": PROJECT_STATUS_LABELS,
            "total_projects": total_projects,
            "risky_projects": risky_projects,
            "workload": workload,
            "avg_progress": avg_progress,
            "notes_this_week": notes_this_week,
            "now": now,
            "unread_count": get_unread_count(current_user, db),
        },
    )
