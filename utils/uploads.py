"""Shared multi-file upload validation."""

from __future__ import annotations

from typing import List, Optional, Tuple

from fastapi import HTTPException, UploadFile

MAX_FILES_PER_UPLOAD = 5


def normalize_upload_files(files: Optional[List[UploadFile]]) -> List[UploadFile]:
    """Normalize multipart file list from the form."""
    if not files:
        return []
    if isinstance(files, UploadFile):
        return [files] if files.filename else []
    return [upload for upload in files if upload and upload.filename]


async def read_validated_files(
    files: Optional[List[UploadFile]], max_upload_bytes: int
) -> List[Tuple[str, str, bytes]]:
    """Read uploads and validate count and size limits.

    Returns a list of (original_filename, content_type, file_bytes).
    """
    real_files = normalize_upload_files(files)
    if len(real_files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(status_code=400, detail="Не более 5 файлов за раз")

    payloads: List[Tuple[str, str, bytes]] = []
    for upload in real_files:
        file_bytes = await upload.read()
        if len(file_bytes) > max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Файл «{upload.filename}» превышает лимит "
                    f"{max_upload_bytes // 1048576}MB"
                ),
            )
        payloads.append(
            (upload.filename, upload.content_type or "application/octet-stream", file_bytes)
        )
    return payloads
