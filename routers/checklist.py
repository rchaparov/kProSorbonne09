"""Project checklist routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import can_write_to_project, get_current_user, get_unread_count
from database import (
    ChecklistItem,
    ChecklistItemAssignee,
    Project,
    ProjectMember,
    User,
    get_db_session,
)
from utils.nav import nav_context

router = APIRouter(tags=["checklist"])
templates = Jinja2Templates(directory="templates")


def _require_user(current_user) -> User:
    """Return authenticated user or redirect response."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    return current_user


def _parse_assignee_ids(assigned_to: Optional[List[int]]) -> List[int]:
    """Normalize form assignee ids to a list of integers."""
    if assigned_to is None:
        return []
    if isinstance(assigned_to, int):
        return [assigned_to]
    return [int(uid) for uid in assigned_to]


def _parse_deadline(value: Optional[str]) -> Optional[datetime]:
    """Parse HTML date input into a datetime."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def _can_edit_item(item: ChecklistItem, user: User) -> bool:
    """Return True if the user may edit the checklist item."""
    return user.system_role == "admin" or item.created_by == user.id


@router.post("/projects/{project_id}/checklist")
async def add_checklist_item(
    project_id: int,
    text: str = Form(...),
    assigned_to: Optional[List[int]] = Form(None),
    deadline: Optional[str] = Form(None),
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
        position=max_pos + 1,
        deadline=_parse_deadline(deadline),
    )
    db.add(item)
    db.flush()

    valid_member_ids = {
        row[0]
        for row in db.query(ProjectMember.user_id).filter_by(project_id=project_id).all()
    }
    for uid in set(_parse_assignee_ids(assigned_to)):
        if uid in valid_member_ids or user.system_role == "admin":
            db.add(ChecklistItemAssignee(item_id=item.id, user_id=uid))

    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.get("/checklist/{item_id}/edit")
async def edit_checklist_item_form(
    item_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the checklist item edit form."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    item = (
        db.query(ChecklistItem)
        .options(joinedload(ChecklistItem.assignees))
        .filter_by(id=item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    if not _can_edit_item(item, user):
        raise HTTPException(status_code=403, detail="Forbidden")

    project = db.query(Project).filter_by(id=item.project_id).first()
    members = (
        db.query(User)
        .join(ProjectMember, User.id == ProjectMember.user_id)
        .filter(ProjectMember.project_id == item.project_id)
        .all()
    )
    current_assignee_ids = {assignee.user_id for assignee in item.assignees}

    return templates.TemplateResponse(
        "checklist_edit.html",
        {
            "request": request,
            "current_user": user,
            "item": item,
            "project": project,
            "members": members,
            "current_assignee_ids": current_assignee_ids,
            "unread_count": get_unread_count(user, db),
            **nav_context(user, db, item.project_id),
        },
    )


@router.post("/checklist/{item_id}/edit")
async def edit_checklist_item(
    item_id: int,
    text: str = Form(...),
    assigned_to: Optional[List[int]] = Form(None),
    deadline: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Update checklist item text, assignees, and deadline."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    item = db.query(ChecklistItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    if not _can_edit_item(item, user):
        raise HTTPException(status_code=403, detail="Forbidden")

    item.text = text.strip()
    item.updated_at = datetime.utcnow()
    item.deadline = _parse_deadline(deadline)

    db.query(ChecklistItemAssignee).filter_by(item_id=item_id).delete()
    db.flush()

    valid_member_ids = {
        row[0]
        for row in db.query(ProjectMember.user_id).filter_by(project_id=item.project_id).all()
    }
    for uid in set(_parse_assignee_ids(assigned_to)):
        if uid in valid_member_ids or user.system_role == "admin":
            db.add(ChecklistItemAssignee(item_id=item.id, user_id=uid))

    db.commit()
    return RedirectResponse(f"/projects/{item.project_id}", status_code=303)


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
    if not _can_edit_item(item, user):
        raise HTTPException(status_code=403, detail="Forbidden")

    project_id = item.project_id
    db.delete(item)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)
