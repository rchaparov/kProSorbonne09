"""Team analytics dashboard routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
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
from main import templates
from utils.analytics_helpers import _sparkline_notes
from utils.nav import nav_context
from utils.progress import PROJECT_STATUS_LABELS, project_progress

router = APIRouter(tags=["analytics"])

STATUS_BAR_COLORS = {
    "planning": "#888780",
    "active": "#378ADD",
    "review": "#BA7517",
    "on_hold": "#D85A30",
    "completed": "#639922",
}


@router.get("/analytics")
async def analytics_page(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render aggregated team analytics for all authenticated users."""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    status_rows = (
        db.query(Project.status, func.count(Project.id))
        .group_by(Project.status)
        .all()
    )
    status_counts = {status: 0 for status in PROJECT_STATUS_LABELS}
    for status, count in status_rows:
        status_counts[status] = count
    total_projects = sum(status_counts.values())
    active_projects_count = sum(
        count for status, count in status_counts.items() if status != "completed"
    )

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

    checklist_totals = dict(
        db.query(ChecklistItem.project_id, func.count(ChecklistItem.id))
        .group_by(ChecklistItem.project_id)
        .all()
    )
    checklist_dones = dict(
        db.query(ChecklistItem.project_id, func.count(ChecklistItem.id))
        .filter(ChecklistItem.is_done.is_(True))
        .group_by(ChecklistItem.project_id)
        .all()
    )

    active_projects = (
        db.query(Project)
        .filter(Project.status.notin_(["completed"]))
        .order_by(Project.title)
        .all()
    )
    progresses = [
        project_progress(
            project.status,
            checklist_dones.get(project.id, 0),
            checklist_totals.get(project.id, 0),
        )
        for project in active_projects
    ]
    avg_progress = round(sum(progresses) / len(progresses)) if progresses else 0

    project_progress_list = []
    for project in active_projects:
        total = checklist_totals.get(project.id, 0)
        done = checklist_dones.get(project.id, 0)
        pct = project_progress(project.status, done, total)
        project_progress_list.append(
            {
                "project": project,
                "pct": pct,
                "done": done,
                "total": total,
                "bar_color": STATUS_BAR_COLORS.get(project.status, "#378ADD"),
            }
        )
    project_progress_list.sort(key=lambda row: row["pct"], reverse=True)

    notes_this_week = (
        db.query(func.count(Note.id)).filter(Note.created_at >= week_ago).scalar()
    ) or 0
    notes_prev_week = (
        db.query(func.count(Note.id))
        .filter(Note.created_at >= two_weeks_ago, Note.created_at < week_ago)
        .scalar()
    ) or 0
    notes_delta = notes_this_week - notes_prev_week

    sparkline_data, sparkline_max = _sparkline_notes(db, now)

    top_authors = (
        db.query(User, func.count(Note.id).label("note_count"))
        .join(Note, Note.author_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Note.id).desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "current_user": current_user,
            "status_counts": status_counts,
            "status_labels": PROJECT_STATUS_LABELS,
            "total_projects": total_projects,
            "active_projects_count": active_projects_count,
            "risky_projects": risky_projects,
            "workload": workload,
            "avg_progress": avg_progress,
            "notes_this_week": notes_this_week,
            "notes_delta": notes_delta,
            "sparkline_data": sparkline_data,
            "sparkline_max": sparkline_max,
            "top_authors": top_authors,
            "project_progress_list": project_progress_list,
            "status_bar_colors": STATUS_BAR_COLORS,
            "now": now,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )
