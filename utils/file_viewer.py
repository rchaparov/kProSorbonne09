"""File viewing utilities."""

from __future__ import annotations

from urllib.parse import quote

from fastapi.responses import HTMLResponse, Response

INLINE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "text/plain",
}

MARKDOWN_TYPES = {"text/markdown", "text/x-markdown"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def _content_disposition_header(disposition: str, filename: str) -> str:
    """Build Content-Disposition header safe for non-ASCII filenames."""
    fallback = filename.encode("ascii", "replace").decode("ascii").replace("?", "_") or "file"
    encoded = quote(filename, safe="")
    return f'{disposition}; filename="{fallback}"; filename*=UTF-8\'\'{encoded}'


def serve_file_for_view(
    file_data: bytes,
    content_type: str,
    original_filename: str,
) -> Response:
    """Return inline Response or HTML-rendered Markdown."""
    if not isinstance(file_data, bytes):
        file_data = bytes(file_data)

    content_type = content_type or ""
    original_filename = original_filename or "file"

    ext = (
        ("." + original_filename.rsplit(".", 1)[-1].lower())
        if "." in original_filename
        else ""
    )

    if content_type in MARKDOWN_TYPES or ext in MARKDOWN_EXTENSIONS:
        import markdown as md_lib

        text = file_data.decode("utf-8", errors="replace")
        body = md_lib.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br", "toc"],
        )
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{original_filename}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 860px; margin: 40px auto; padding: 0 24px;
         color: #1f2937; line-height: 1.7; background: #f9fafb; }}
  h1,h2,h3,h4 {{ color: #111827; margin-top: 1.5em; }}
  h1 {{ font-size: 1.75rem; border-bottom: 2px solid #e5e7eb; padding-bottom: .4em; }}
  h2 {{ font-size: 1.35rem; border-bottom: 1px solid #e5e7eb; padding-bottom: .3em; }}
  a {{ color: #4f46e5; }}
  code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 4px;
          font-size: .875em; font-family: "JetBrains Mono", monospace; }}
  pre {{ background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px;
         overflow-x: auto; font-size: .875em; }}
  pre code {{ background: none; padding: 0; color: inherit; }}
  blockquote {{ border-left: 4px solid #6366f1; margin: 0; padding: 4px 16px;
                color: #6b7280; background: #f5f3ff; border-radius: 0 6px 6px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th,td {{ border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }}
  th {{ background: #f3f4f6; font-weight: 600; }}
  img {{ max-width: 100%; height: auto; border-radius: 6px; }}
</style>
</head>
<body>{body}</body>
</html>"""
        return HTMLResponse(content=html)

    if content_type in INLINE_TYPES:
        return Response(
            content=file_data,
            media_type=content_type,
            headers={
                "Content-Disposition": _content_disposition_header("inline", original_filename),
                "Cache-Control": "no-store",
            },
        )

    return Response(
        content=file_data,
        media_type=content_type or "application/octet-stream",
        headers={
            "Content-Disposition": _content_disposition_header("attachment", original_filename),
        },
    )
