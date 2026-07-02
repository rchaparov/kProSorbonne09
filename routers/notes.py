"""Note and attachment routes."""

from datetime import datetime
from typing import List, Optional
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session as DbSession

from auth import can_write_to_project, get_current_user, get_unread_count
from config import settings
from database import (
    Material,
    Note,
    NoteAttachment,
    NoteMaterialLink,
    NoteMention,
    Notification,
    Project,
    ProjectMember,
    User,
    get_db_session,
)
from main import templates
from utils.file_viewer import serve_file_for_view
from utils.nav import nav_context
from utils.uploads import read_validated_files

router = APIRouter(tags=["notes"])

INLINE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


def _attachment_disposition(content_type: str) -> str:
    """Return inline disposition for PDF/images, attachment otherwise."""
    if content_type == "application/pdf" or content_type.startswith("image/"):
        return "inline"
    if content_type in INLINE_TYPES:
        return "inline"
    return "attachment"


def _content_disposition_header(disposition: str, filename: str) -> str:
    """Build Content-Disposition header safe for non-ASCII filenames."""
    fallback = filename.encode("ascii", "replace").decode("ascii").replace("?", "_") or "file"
    encoded = quote(filename, safe="")
    return f"{disposition}; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"


def _attachment_bytes(file_data) -> bytes:
    """Normalize attachment binary payload to bytes."""
    if isinstance(file_data, bytes):
        return file_data
    return bytes(file_data)


def _can_delete_note(note: Note, user: User) -> bool:
    """Return True if the user may delete the given note."""
    return user.system_role == "admin" or note.author_id == user.id


def _can_edit_note(note: Note, user: User) -> bool:
    """Return True if the user may edit the given note."""
    return user.system_role == "admin" or note.author_id == user.id


def _can_access_note_attachment(
    attachment: NoteAttachment, user: User, db: DbSession
) -> bool:
    """Return True if the user may read a note attachment."""
    note = db.query(Note).filter_by(id=attachment.note_id).first()
    if not note:
        return False
    if user.system_role in ("admin", "coordinator"):
        return True
    return (
        db.query(ProjectMember)
        .filter_by(project_id=note.project_id, user_id=user.id)
        .first()
        is not None
    )


def _add_attachments_from_payloads(
    note_id: int, payloads: List[tuple], db: DbSession
) -> None:
    """Create NoteAttachment rows from validated file payloads."""
    for original_filename, content_type, file_bytes in payloads:
        db.add(
            NoteAttachment(
                note_id=note_id,
                filename=str(uuid4()),
                original_filename=original_filename,
                file_size=len(file_bytes),
                content_type=content_type,
                file_data=file_bytes,
            )
        )


@router.post("/projects/{project_id}/notes")
async def create_note(
    project_id: int,
    content: str = Form(...),
    parent_id: Optional[int] = Form(None),
    quoted_content: Optional[str] = Form(None),
    mentions: Optional[List[int]] = Form(None),
    material_ids: List[int] = Form(default=[]),
    files: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Create a note in a project with optional files and member mentions."""
    if not can_write_to_project(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    file_payloads = await read_validated_files(files, settings.MAX_UPLOAD_BYTES)

    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    validated_parent_id = None
    if parent_id:
        parent = db.query(Note).filter_by(id=parent_id, project_id=project_id).first()
        if parent:
            if parent.parent_id is not None:
                validated_parent_id = parent.parent_id
            else:
                validated_parent_id = parent_id

    note = Note(
        project_id=project_id,
        author_id=current_user.id,
        content=content,
        parent_id=validated_parent_id,
        quoted_content=quoted_content[:300] if quoted_content else None,
    )
    db.add(note)
    db.flush()

    mention_ids: List[int] = []
    if mentions is not None:
        if isinstance(mentions, int):
            mention_ids = [mentions]
        else:
            mention_ids = [int(m) for m in mentions]

    _add_attachments_from_payloads(note.id, file_payloads, db)

    for user_id in mention_ids:
        if user_id == current_user.id:
            continue
        db.add(NoteMention(note_id=note.id, user_id=user_id))
        db.add(
            Notification(
                user_id=user_id,
                note_id=note.id,
                project_id=project_id,
                message=f"{current_user.full_name} упомянул вас в проекте «{project.title}»",
            )
        )

    for material_id in set(material_ids):
        if db.query(Material).filter_by(id=material_id).first():
            db.add(NoteMaterialLink(note_id=note.id, material_id=material_id))

    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.get("/notes/{note_id}/edit")
async def edit_note_form(
    note_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the note edit form for author or admin."""
    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not _can_edit_note(note, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    project = db.query(Project).filter_by(id=note.project_id).first()
    return templates.TemplateResponse(
        "note_edit.html",
        {
            "request": request,
            "current_user": current_user,
            "note": note,
            "project": project,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db, note.project_id),
        },
    )


@router.post("/notes/{note_id}/edit")
async def edit_note(
    note_id: int,
    content: str = Form(...),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Update note content and redirect to the project page."""
    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not _can_edit_note(note, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    note.content = content
    note.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/projects/{note.project_id}", status_code=303)


@router.post("/notes/{note_id}/delete")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a note and its attachments, then redirect to the project page."""
    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not _can_delete_note(note, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    project_id = note.project_id
    db.delete(note)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.delete("/notes/{note_id}")
async def delete_note_api(
    note_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a note via HTTP DELETE."""
    return await delete_note(note_id, current_user, db)


@router.post("/notes/{note_id}/attachments")
async def upload_attachment(
    note_id: int,
    files: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Upload file attachments to a note."""
    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not can_write_to_project(note.project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    file_payloads = await read_validated_files(files, settings.MAX_UPLOAD_BYTES)
    if not file_payloads:
        raise HTTPException(status_code=400, detail="Выберите хотя бы один файл")

    _add_attachments_from_payloads(note_id, file_payloads, db)
    db.commit()
    return RedirectResponse(f"/projects/{note.project_id}", status_code=303)


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Download a note attachment."""
    attachment = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if not _can_access_note_attachment(attachment, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    return Response(
        content=_attachment_bytes(attachment.file_data),
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": _content_disposition_header(
                "attachment", attachment.original_filename
            ),
        },
    )


@router.get("/attachments/{attachment_id}/view")
async def view_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """View a note attachment inline when supported by the browser."""
    attachment = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if not _can_access_note_attachment(attachment, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    return serve_file_for_view(
        _attachment_bytes(attachment.file_data),
        attachment.content_type,
        attachment.original_filename,
    )


@router.post("/attachments/{attachment_id}/delete")
async def delete_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a note attachment and redirect to the project page."""
    attachment = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    note = db.query(Note).filter_by(id=attachment.note_id).first()
    if not note or not _can_delete_note(note, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    project_id = note.project_id
    db.delete(attachment)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.delete("/attachments/{attachment_id}")
async def delete_attachment_api(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete an attachment via HTTP DELETE."""
    return await delete_attachment(attachment_id, current_user, db)
