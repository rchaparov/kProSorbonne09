"""Project detail routes."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DbSession

from auth import can_write_to_project, get_current_user, get_unread_count
from database import Note, NoteAttachment, NoteMention, Project, ProjectMember, User, get_db_session

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
        .order_by(Note.created_at.desc())
        .all()
    )
    note_items = []
    for note in notes:
        author = db.query(User).filter_by(id=note.author_id).first()
        attachments = db.query(NoteAttachment).filter_by(note_id=note.id).all()
        mention_rows = db.query(NoteMention).filter_by(note_id=note.id).all()
        mentioned_users = []
        for mention in mention_rows:
            mentioned = db.query(User).filter_by(id=mention.user_id).first()
            if mentioned:
                mentioned_users.append(mentioned)
        note_items.append(
            {
                "note": note,
                "author": author,
                "attachments": attachments,
                "mentions": mentioned_users,
            }
        )

    memberships = db.query(ProjectMember).filter_by(project_id=project_id).all()
    members = []
    for membership in memberships:
        user = db.query(User).filter_by(id=membership.user_id).first()
        if user:
            members.append(user)

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
