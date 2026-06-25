"""Dashboard routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session as DbSession

from auth import get_current_user, get_unread_count
from database import ChecklistItem, Project, ProjectMember, User, get_db_session

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def dashboard(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the project list for all authenticated users."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    projects = db.query(Project).order_by(Project.created_at.desc()).all()
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

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "projects": projects,
            "member_counts": member_counts,
            "checklist_stats": checklist_stats,
            "now": datetime.utcnow(),
            "unread_count": get_unread_count(current_user, db),
        },
    )
