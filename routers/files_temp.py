"""Temporary public file tokens for Office Online Viewer."""

from datetime import datetime, timedelta
from typing import Union
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from auth import get_current_user
from config import settings
from database import MaterialFile, NoteAttachment, TempFileToken, User, get_db_session
from utils.file_viewer import serve_file_for_view

router = APIRouter(tags=["files_temp"])

TTL_MINUTES = 5


class TempTokenRequest(BaseModel):
    """Request body for creating a temporary file access token."""

    file_type: str
    file_id: int


def _content_disposition_header(disposition: str, filename: str) -> str:
    """Build Content-Disposition header safe for non-ASCII filenames."""
    fallback = filename.encode("ascii", "replace").decode("ascii").replace("?", "_") or "file"
    encoded = quote(filename, safe="")
    return f"{disposition}; filename=\"{fallback}\"; filename*=UTF-8''{encoded}"


def _file_bytes(file_data) -> bytes:
    """Normalize binary payload to bytes."""
    if isinstance(file_data, bytes):
        return file_data
    return bytes(file_data)


def _load_file(file_type: str, file_id: int, db: DbSession):
    """Load note attachment or material file by type and id."""
    if file_type == "note_attachment":
        return db.query(NoteAttachment).filter_by(id=file_id).first()
    if file_type == "material_file":
        return db.query(MaterialFile).filter_by(id=file_id).first()
    return None


@router.post("/files/temp")
async def create_temp_token(
    body: TempTokenRequest,
    current_user: Union[User, RedirectResponse] = Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Create a short-lived public token for Office Online Viewer."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    if not settings.BASE_URL:
        raise HTTPException(status_code=503, detail="Office viewer not configured")

    file_obj = _load_file(body.file_type, body.file_id, db)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    if body.file_type not in ("note_attachment", "material_file"):
        raise HTTPException(status_code=400, detail="Invalid file_type")

    token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=TTL_MINUTES)

    db.add(
        TempFileToken(
            token=token,
            file_type=body.file_type,
            file_id=body.file_id,
            expires_at=expires_at,
        )
    )
    db.commit()

    public_url = f"{settings.BASE_URL}/files/temp/{token}"
    viewer_url = (
        f"https://view.officeapps.live.com/op/view.aspx?src={quote(public_url, safe='')}"
    )

    return JSONResponse({"token": token, "viewer_url": viewer_url})


@router.get("/files/temp/{token}")
async def serve_temp_file(token: str, db: DbSession = Depends(get_db_session)):
    """Serve a file publicly for Office Online Viewer (no auth required)."""
    record = db.query(TempFileToken).filter_by(token=token).first()
    if not record:
        raise HTTPException(status_code=404, detail="Token not found")
    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Token expired")

    file_obj = _load_file(record.file_type, record.file_id, db)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    return serve_file_for_view(
        _file_bytes(file_obj.file_data),
        file_obj.content_type,
        file_obj.original_filename,
    )
