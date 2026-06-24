"""Note and attachment routes."""

from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session as DbSession

from auth import can_write_to_project, get_current_user
from config import settings
from database import Note, NoteAttachment, User, get_db_session

router = APIRouter(tags=["notes"])


def _require_user(current_user) -> User:
    """Ensure the dependency resolved to an authenticated user."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    return current_user


def _can_delete_note(note: Note, user: User) -> bool:
    """Return True if the user may delete the given note."""
    return user.system_role == "admin" or note.author_id == user.id


@router.post("/projects/{project_id}/notes")
async def create_note(
    project_id: int,
    content: str = Form(...),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Create a note in a project and redirect to the project page."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    if not can_write_to_project(project_id, user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    note = Note(project_id=project_id, author_id=user.id, content=content)
    db.add(note)
    db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@router.post("/notes/{note_id}/delete")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a note and its attachments, then redirect to the project page."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not _can_delete_note(note, user):
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
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Upload a file attachment to a note."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if not can_write_to_project(note.project_id, user, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Файл превышает лимит {settings.MAX_UPLOAD_BYTES // 1048576}MB",
        )

    attachment = NoteAttachment(
        note_id=note_id,
        filename=str(uuid4()),
        original_filename=file.filename or "file",
        file_size=len(file_bytes),
        content_type=file.content_type or "application/octet-stream",
        file_data=file_bytes,
    )
    db.add(attachment)
    db.commit()
    return RedirectResponse(f"/projects/{note.project_id}", status_code=303)


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Download a note attachment."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    attachment = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return Response(
        content=attachment.file_data,
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.original_filename}"',
        },
    )


@router.post("/attachments/{attachment_id}/delete")
async def delete_attachment(
    attachment_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a note attachment and redirect to the project page."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    attachment = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    note = db.query(Note).filter_by(id=attachment.note_id).first()
    if not note or not _can_delete_note(note, user):
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
