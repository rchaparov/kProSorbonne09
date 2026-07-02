"""Global search routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_current_user, get_unread_count
from database import Material, Note, Project, ProjectMember, User, get_db_session
from main import templates
from utils.nav import nav_context

router = APIRouter(tags=["search"])


def _accessible_project_ids(user: User, db: DbSession) -> list[int] | None:
    """Return project IDs visible to the user, or None for admin (all projects)."""
    if user.system_role in ("admin", "coordinator"):
        return None
    rows = db.query(ProjectMember.project_id).filter_by(user_id=user.id).all()
    return [row[0] for row in rows]


@router.get("/search")
async def search(
    request: Request,
    q: str = "",
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Search projects, notes, and materials."""
    query = q.strip()
    results = {"projects": [], "notes": [], "materials": []}

    if len(query) >= 2:
        like = f"%{query}%"
        project_ids = _accessible_project_ids(current_user, db)

        projects_query = db.query(Project).filter(Project.title.ilike(like))
        if project_ids is not None:
            if project_ids:
                projects_query = projects_query.filter(Project.id.in_(project_ids))
            else:
                projects_query = projects_query.filter(False)
        results["projects"] = projects_query.order_by(Project.created_at.desc()).limit(10).all()

        notes_query = (
            db.query(Note)
            .options(joinedload(Note.project), joinedload(Note.author))
            .filter(Note.content.ilike(like))
        )
        results["notes"] = notes_query.order_by(Note.created_at.desc()).limit(10).all()

        results["materials"] = (
            db.query(Material)
            .options(joinedload(Material.author))
            .filter(
                or_(
                    Material.title.ilike(like),
                    Material.description.ilike(like),
                )
            )
            .order_by(Material.created_at.desc())
            .limit(10)
            .all()
        )

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "current_user": current_user,
            "q": query,
            "results": results,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )
