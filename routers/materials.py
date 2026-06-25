"""Shared knowledge base materials routes."""

from typing import Optional
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_current_user, get_unread_count
from config import settings
from database import MATERIAL_CATEGORIES, Material, MaterialFile, User, get_db_session
from utils.file_viewer import serve_file_for_view

router = APIRouter(tags=["materials"])
templates = Jinja2Templates(directory="templates")

INLINE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


def _require_user(current_user):
    """Return authenticated user or redirect response."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    return current_user


def _file_disposition(content_type: str) -> str:
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


def _file_bytes(file_data) -> bytes:
    """Normalize file binary payload to bytes."""
    if isinstance(file_data, bytes):
        return file_data
    return bytes(file_data)


def _can_delete_material(material: Material, user: User) -> bool:
    """Return True if the user may delete the material."""
    return user.system_role == "admin" or material.added_by == user.id


def _load_material_items(materials: list[Material]) -> list[dict]:
    """Attach author and files to each material."""
    return [
        {
            "material": material,
            "author": material.author,
            "files": material.files,
        }
        for material in materials
    ]


@router.get("/materials")
async def materials_list(
    request: Request,
    category: str | None = None,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render materials grouped by category with optional filter."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    query = (
        db.query(Material)
        .options(joinedload(Material.author), joinedload(Material.files))
        .order_by(Material.created_at.desc())
    )
    active_category = category if category in MATERIAL_CATEGORIES else None
    if active_category:
        query = query.filter_by(category=active_category)

    material_items = _load_material_items(query.all())
    grouped: dict[str, list[dict]] = {cat: [] for cat in MATERIAL_CATEGORIES}
    for item in material_items:
        cat = item["material"].category
        if cat in grouped:
            grouped[cat].append(item)

    return templates.TemplateResponse(
        "materials.html",
        {
            "request": request,
            "current_user": user,
            "categories": MATERIAL_CATEGORIES,
            "category": active_category,
            "grouped": grouped,
            "material_items": material_items,
            "msg": request.query_params.get("msg"),
            "unread_count": get_unread_count(user, db),
            "office_viewer_enabled": bool(settings.BASE_URL),
        },
    )


@router.get("/materials/new")
async def material_new_form(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the new material form."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    return templates.TemplateResponse(
        "material_form.html",
        {
            "request": request,
            "current_user": user,
            "categories": MATERIAL_CATEGORIES,
            "unread_count": get_unread_count(user, db),
        },
    )


@router.post("/materials/new")
async def material_create(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("Другое"),
    url: str = Form(""),
    file: Optional[UploadFile] = File(default=None),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Create a new knowledge base material."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    if category not in MATERIAL_CATEGORIES:
        category = "Другое"

    material = Material(
        title=title,
        description=description or None,
        category=category,
        url=url or None,
        added_by=user.id,
    )
    db.add(material)
    db.flush()

    if file and file.filename:
        file_bytes = await file.read()
        if len(file_bytes) > settings.MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Файл превышает лимит {settings.MAX_UPLOAD_BYTES // 1048576}MB",
            )
        db.add(
            MaterialFile(
                material_id=material.id,
                filename=str(uuid4()),
                original_filename=file.filename,
                file_size=len(file_bytes),
                content_type=file.content_type or "application/octet-stream",
                file_data=file_bytes,
            )
        )

    db.commit()
    return RedirectResponse("/materials?msg=added", status_code=303)


@router.post("/materials/{material_id}/delete")
async def material_delete(
    material_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a material if permitted."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    material = db.query(Material).filter_by(id=material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not _can_delete_material(material, user):
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(material)
    db.commit()
    return RedirectResponse("/materials?msg=deleted", status_code=303)


@router.get("/materials/{material_id}/files/{file_id}/download")
async def material_file_download(
    material_id: int,
    file_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Download a material file."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    material_file = (
        db.query(MaterialFile)
        .filter_by(id=file_id, material_id=material_id)
        .first()
    )
    if not material_file:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=_file_bytes(material_file.file_data),
        media_type=material_file.content_type,
        headers={
            "Content-Disposition": _content_disposition_header(
                "attachment", material_file.original_filename
            ),
        },
    )


@router.get("/materials/{material_id}/files/{file_id}/view")
async def material_file_view(
    material_id: int,
    file_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """View a material file inline when supported."""
    user = _require_user(current_user)
    if isinstance(user, RedirectResponse):
        return user

    material_file = (
        db.query(MaterialFile)
        .filter_by(id=file_id, material_id=material_id)
        .first()
    )
    if not material_file:
        raise HTTPException(status_code=404, detail="File not found")

    return serve_file_for_view(
        _file_bytes(material_file.file_data),
        material_file.content_type,
        material_file.original_filename,
    )
