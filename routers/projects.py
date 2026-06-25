"""Project detail routes."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import can_write_to_project, get_current_user, get_unread_count
from database import Note, NoteMention, Project, ProjectMember, get_db_session

router = APIRouter(tags=["projects"])
templates = Jinja2Templates(directory="templates")


@router.get("/projects/{project_id}")
async def project_detail(
    project_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render project details, members, and notes feed."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    notes = (
        db.query(Note)
        .filter_by(project_id=project_id)
        .options(
            joinedload(Note.author),
            joinedload(Note.attachments),
            joinedload(Note.mentions).joinedload(NoteMention.user),
        )
        .order_by(Note.created_at.desc())
        .all()
    )
    note_items = []
    for note in notes:
        mentioned_users = [mention.user for mention in note.mentions if mention.user]
        note_items.append(
            {
                "note": note,
                "author": note.author,
                "attachments": note.attachments,
                "mentions": mentioned_users,
            }
        )

    memberships = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id)
        .options(joinedload(ProjectMember.user))
        .all()
    )
    members = [membership.user for membership in memberships if membership.user]

    can_write = can_write_to_project(project_id, current_user, db)

    members_json = json.dumps(
        [{"id": m.id, "name": m.full_name} for m in members],
        ensure_ascii=False,
    )

    return templates.TemplateResponse(
        "project_detail.html",
        {
            "request": request,
            "current_user": current_user,
            "project": project,
            "note_items": note_items,
            "members": members,
            "members_json": members_json,
            "can_write": can_write,
            "now": datetime.utcnow(),
            "unread_count": get_unread_count(current_user, db),
        },
    )
