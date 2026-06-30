"""Navigation helpers: recent projects for navbar dropdown."""

from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from database import Project, ProjectMember, User


def get_recent_projects(user: User, db: DbSession, limit: int = 8) -> list[Project]:
    """Return up to `limit` projects ordered by updated_at (most recent first)."""
    if user.system_role in ("admin", "coordinator"):
        return (
            db.query(Project)
            .order_by(Project.updated_at.desc())
            .limit(limit)
            .all()
        )

    member_ids = {
        row[0]
        for row in db.query(ProjectMember.project_id).filter_by(user_id=user.id).all()
    }
    if not member_ids:
        return []

    return (
        db.query(Project)
        .filter(Project.id.in_(member_ids))
        .order_by(Project.updated_at.desc())
        .limit(limit)
        .all()
    )


def nav_context(
    user: User,
    db: DbSession,
    current_project_id: int | None = None,
) -> dict:
    """Build template context for navbar project switcher."""
    return {
        "recent_projects": get_recent_projects(user, db),
        "current_project_id": current_project_id,
    }
