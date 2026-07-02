"""Note feed polling API."""

from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_current_user
from database import Note, NoteMention, get_db_session

router = APIRouter(tags=["feed"])

PAGE_SIZE = 20


def _author_initials(author) -> str:
    """Return two-letter initials from author full name."""
    parts = (author.full_name if author else "").split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    if parts:
        return parts[0][0].upper()
    return "?"


def _serialize_reply(reply: Note) -> dict:
    """Serialize a reply note for the feed JSON."""
    author = reply.author
    return {
        "id": reply.id,
        "content": reply.content,
        "quoted_content": reply.quoted_content,
        "author_name": author.full_name if author else "—",
        "author_initials": _author_initials(author),
        "created_at": reply.created_at.isoformat(),
        "mentions": [],
        "attachments": [],
        "replies": [],
    }


def _serialize_note(note: Note, replies: list) -> dict:
    """Serialize a root note with its new replies for the feed JSON."""
    author = note.author
    return {
        "id": note.id,
        "content": note.content,
        "quoted_content": note.quoted_content,
        "author_name": author.full_name if author else "—",
        "author_initials": _author_initials(author),
        "created_at": note.created_at.isoformat(),
        "mentions": [m.user.full_name for m in note.mentions if m.user],
        "attachments": [
            {"id": attachment.id, "original_filename": attachment.original_filename}
            for attachment in note.attachments
        ],
        "replies": [_serialize_reply(reply) for reply in replies],
    }


@router.get("/projects/{project_id}/notes/feed")
async def notes_feed(
    project_id: int,
    after: str,
    page: int = 1,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Return new root notes and replies on page 1 created after the given timestamp."""
    if page != 1:
        return JSONResponse({"notes": [], "count": 0, "latest_at": None})

    try:
        after_dt = datetime.fromisoformat(after)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid after timestamp") from exc

    page_root_ids = [
        row[0]
        for row in (
            db.query(Note.id)
            .filter(Note.project_id == project_id, Note.parent_id.is_(None))
            .order_by(Note.created_at.desc())
            .limit(PAGE_SIZE)
            .all()
        )
    ]

    new_root_notes = (
        db.query(Note)
        .options(
            joinedload(Note.author),
            joinedload(Note.attachments),
            joinedload(Note.mentions).joinedload(NoteMention.user),
        )
        .filter(
            Note.project_id == project_id,
            Note.parent_id.is_(None),
            Note.created_at > after_dt,
        )
        .order_by(Note.created_at.desc())
        .limit(50)
        .all()
    )

    new_replies = []
    if page_root_ids:
        new_replies = (
            db.query(Note)
            .options(joinedload(Note.author))
            .filter(
                Note.parent_id.in_(page_root_ids),
                Note.created_at > after_dt,
            )
            .order_by(Note.created_at.asc())
            .all()
        )

    replies_by_parent: dict = defaultdict(list)
    for reply in new_replies:
        replies_by_parent[reply.parent_id].append(reply)

    new_root_ids = {note.id for note in new_root_notes}
    roots_with_reply_only = [
        parent_id
        for parent_id in replies_by_parent
        if parent_id not in new_root_ids
    ]

    existing_roots = []
    if roots_with_reply_only:
        existing_roots = (
            db.query(Note)
            .options(
                joinedload(Note.author),
                joinedload(Note.attachments),
                joinedload(Note.mentions).joinedload(NoteMention.user),
            )
            .filter(Note.id.in_(roots_with_reply_only))
            .all()
        )

    all_roots = new_root_notes + existing_roots
    all_roots.sort(key=lambda note: note.created_at, reverse=True)

    serialized = [
        _serialize_note(note, replies_by_parent.get(note.id, []))
        for note in all_roots
    ]

    all_new = list(new_root_notes) + list(new_replies)
    latest_at = max(note.created_at for note in all_new).isoformat() if all_new else None

    return JSONResponse(
        {
            "notes": serialized,
            "count": len(new_root_notes) + len(new_replies),
            "latest_at": latest_at,
        }
    )
