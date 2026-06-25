"""Project detail routes."""

import json
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import can_write_to_project, get_current_user, get_unread_count
from config import settings
from database import (
    ChecklistItem,
    Material,
    Note,
    NoteMaterialLink,
    NoteMention,
    Project,
    ProjectMember,
    get_db_session,
)

router = APIRouter(tags=["projects"])
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 20


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

    page = max(1, int(request.query_params.get("page", 1)))
    offset = (page - 1) * PAGE_SIZE

    total_roots = (
        db.query(func.count(Note.id))
        .filter_by(project_id=project_id, parent_id=None)
        .scalar()
    ) or 0

    root_notes = (
        db.query(Note)
        .filter_by(project_id=project_id, parent_id=None)
        .options(
            joinedload(Note.author),
            joinedload(Note.attachments),
            joinedload(Note.mentions).joinedload(NoteMention.user),
            joinedload(Note.material_links).joinedload(NoteMaterialLink.material),
        )
        .order_by(Note.created_at.desc())
        .offset(offset)
        .limit(PAGE_SIZE)
        .all()
    )

    root_ids = [note.id for note in root_notes]
    if root_ids:
        replies = (
            db.query(Note)
            .options(joinedload(Note.author))
            .filter(Note.parent_id.in_(root_ids))
            .order_by(Note.created_at.asc())
            .all()
        )
    else:
        replies = []

    replies_by_parent: dict = defaultdict(list)
    for reply in replies:
        replies_by_parent[reply.parent_id].append(reply)

    note_items = []
    for note in root_notes:
        mentioned_users = [mention.user for mention in note.mentions if mention.user]
        linked_materials = [
            link.material for link in note.material_links if link.material
        ]
        note_items.append(
            {
                "note": note,
                "author": note.author,
                "attachments": note.attachments,
                "mentions": mentioned_users,
                "linked_materials": linked_materials,
                "replies": replies_by_parent.get(note.id, []),
            }
        )

    total_pages = (total_roots + PAGE_SIZE - 1) // PAGE_SIZE if total_roots else 1
    notes_from = offset + 1 if total_roots else 0
    notes_to = min(page * PAGE_SIZE, total_roots)

    memberships = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id)
        .options(joinedload(ProjectMember.user))
        .all()
    )
    members = [membership.user for membership in memberships if membership.user]

    checklist_items = (
        db.query(ChecklistItem)
        .filter_by(project_id=project_id)
        .options(joinedload(ChecklistItem.assigned_user))
        .order_by(ChecklistItem.position)
        .all()
    )
    checklist_total = len(checklist_items)
    checklist_done = sum(1 for item in checklist_items if item.is_done)

    all_materials = (
        db.query(Material)
        .order_by(Material.category, Material.title)
        .all()
    )

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
            "checklist_items": checklist_items,
            "checklist_total": checklist_total,
            "checklist_done": checklist_done,
            "all_materials": all_materials,
            "can_write": can_write,
            "office_viewer_enabled": bool(settings.BASE_URL),
            "now": datetime.utcnow(),
            "unread_count": get_unread_count(current_user, db),
            "page": page,
            "total_pages": total_pages,
            "total_roots": total_roots,
            "notes_from": notes_from,
            "notes_to": notes_to,
            "page_size": PAGE_SIZE,
        },
    )
