"""Project checklist routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from auth import can_write_to_project, get_current_user
from database import ChecklistItem, Project, ProjectMember, User, get_db_session

router = APIRouter(tags=["checklist"])


def _require_user(current_user) -> User:
    """Return authenticated user or redirect response."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    return current_user


def _validate_assignee(project_id: int, assigned_to: Optional[int], db: DbSession) -> Optional[int]:
    """Return user id if assignee is a project member, else None."""
    if not assigned_to:
        return None
    membership = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=assigned_to)
        .first()
    )
    return assigned_to if membership else None


@router.post("/projects/{project_id}/checklist")
async def add_checklist_item(
    project_id: int,
    text: str = Form(...),
    assigned_to: Optional[int] = Form(None),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Add a checklist item to a project."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    if not can_write_to_project(project_id, user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    max_pos = (
        db.query(func.max(ChecklistItem.position))
        .filter_by(project_id=project_id)
        .scalar()
    ) or 0

    item = ChecklistItem(
        project_id=project_id,
        text=text.strip(),
        created_by=user.id,
        assigned_to=_validate_assignee(project_id, assigned_to, db),
        position=max_pos + 1,
    )
    db.add(item)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.post("/checklist/{item_id}/toggle")
async def toggle_checklist_item(
    item_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Toggle checklist item done state."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    item = db.query(ChecklistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    if not can_write_to_project(item.project_id, user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    item.is_done = not item.is_done
    item.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/projects/{item.project_id}", status_code=303)


@router.post("/checklist/{item_id}/delete")
async def delete_checklist_item(
    item_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a checklist item if permitted."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    item = db.query(ChecklistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    if user.system_role != "admin" and item.created_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    project_id = item.project_id
    db.delete(item)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)
