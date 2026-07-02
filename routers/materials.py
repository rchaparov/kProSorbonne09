"""Shared knowledge base materials routes."""

from typing import List
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, joinedload

from auth import get_current_user, get_unread_count
from config import settings
from database import (
    MATERIAL_CATEGORIES,
    Material,
    MaterialFile,
    NoteMaterialLink,
    User,
    get_db_session,
)
from main import templates
from utils.file_viewer import serve_file_for_view
from utils.nav import nav_context
from utils.uploads import read_validated_files

router = APIRouter(tags=["materials"])

INLINE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


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


def _load_material_items(materials: list[Material], usage_counts: dict[int, int]) -> list[dict]:
    """Attach author, files, and usage count to each material."""
    return [
        {
            "material": material,
            "author": material.author,
            "files": material.files,
            "usage_count": usage_counts.get(material.id, 0),
        }
        for material in materials
    ]


def _add_material_files(
    material_id: int,
    payloads: list[tuple[str, str, bytes]],
    db: DbSession,
) -> None:
    """Create MaterialFile rows from validated file payloads."""
    for original_filename, content_type, file_bytes in payloads:
        db.add(
            MaterialFile(
                material_id=material_id,
                filename=str(uuid4()),
                original_filename=original_filename,
                file_size=len(file_bytes),
                content_type=content_type,
                file_data=file_bytes,
            )
        )


@router.get("/materials")
async def materials_list(
    request: Request,
    category: str | None = None,
    mine: int | None = None,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render materials grouped by category with optional filter."""
    query = (
        db.query(Material)
        .options(joinedload(Material.author), joinedload(Material.files))
        .order_by(Material.created_at.desc())
    )
    active_category = category if category in MATERIAL_CATEGORIES else None
    if active_category:
        query = query.filter_by(category=active_category)
    mine_only = bool(mine)
    if mine_only:
        query = query.filter_by(added_by=current_user.id)

    materials = query.all()

    usage_counts = dict(
        db.query(NoteMaterialLink.material_id, func.count(NoteMaterialLink.id))
        .group_by(NoteMaterialLink.material_id)
        .all()
    )

    material_items = _load_material_items(materials, usage_counts)
    grouped: dict[str, list[dict]] = {cat: [] for cat in MATERIAL_CATEGORIES}
    for item in material_items:
        cat = item["material"].category
        if cat in grouped:
            grouped[cat].append(item)

    return templates.TemplateResponse(
        "materials.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": MATERIAL_CATEGORIES,
            "category": active_category,
            "grouped": grouped,
            "material_items": material_items,
            "mine_only": mine_only,
            "msg": request.query_params.get("msg"),
            "unread_count": get_unread_count(current_user, db),
            "office_viewer_enabled": bool(settings.BASE_URL),
            **nav_context(current_user, db),
        },
    )


@router.get("/materials/new")
async def material_new_form(
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the new material form."""
    return templates.TemplateResponse(
        "material_form.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": MATERIAL_CATEGORIES,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )


@router.post("/materials/new")
async def material_create(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("Другое"),
    url: str = Form(""),
    files: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Create a new knowledge base material."""
    payloads = await read_validated_files(files, settings.MAX_UPLOAD_BYTES)

    title = title.strip()
    description = description.strip()

    if category not in MATERIAL_CATEGORIES:
        category = "Другое"

    material = Material(
        title=title,
        description=description or None,
        category=category,
        url=url or None,
        added_by=current_user.id,
    )
    db.add(material)
    db.flush()

    _add_material_files(material.id, payloads, db)

    db.commit()
    return RedirectResponse("/materials?msg=added", status_code=303)


@router.get("/materials/{material_id}/edit")
async def material_edit_form(
    material_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Render the material edit form."""
    material = db.query(Material).filter_by(id=material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not _can_delete_material(material, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    return templates.TemplateResponse(
        "material_edit.html",
        {
            "request": request,
            "current_user": current_user,
            "material": material,
            "categories": MATERIAL_CATEGORIES,
            "unread_count": get_unread_count(current_user, db),
            **nav_context(current_user, db),
        },
    )


@router.post("/materials/{material_id}/edit")
async def material_edit(
    material_id: int,
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("Другое"),
    url: str = Form(""),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Update material metadata."""
    material = db.query(Material).filter_by(id=material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not _can_delete_material(material, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    title = title.strip()
    description = description.strip()

    material.title = title
    material.description = description or None
    material.category = category if category in MATERIAL_CATEGORIES else "Другое"
    material.url = url or None
    db.commit()
    return RedirectResponse("/materials?msg=updated", status_code=303)


@router.post("/materials/{material_id}/files")
async def material_add_files(
    material_id: int,
    files: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Add files to an existing material."""
    material = db.query(Material).filter_by(id=material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not _can_delete_material(material, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    payloads = await read_validated_files(files, settings.MAX_UPLOAD_BYTES)
    if not payloads:
        raise HTTPException(status_code=400, detail="Выберите хотя бы один файл")

    _add_material_files(material_id, payloads, db)
    db.commit()
    return RedirectResponse("/materials?msg=files_added", status_code=303)


@router.post("/materials/{material_id}/delete")
async def material_delete(
    material_id: int,
    current_user=Depends(get_current_user),
    db: DbSession = Depends(get_db_session),
):
    """Delete a material if permitted."""
    material = db.query(Material).filter_by(id=material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not _can_delete_material(material, current_user):
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
