"""
Smoke tests for TeamSpace.
Run: python tests/smoke_test.py
Requires: app running locally on localhost:8000
OR run in-process: python tests/smoke_test.py --in-process
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# CSS class consistency check (no server required)
# ---------------------------------------------------------------------------

def check_css_classes() -> list[str]:
    """Find CSS classes used in templates but not defined in style.css."""
    style_css = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")
    defined = set(re.findall(r"\.([\w-]+)(?:\s*[,{])", style_css))

    tailwind_prefixes = (
        "bg-", "text-", "flex", "grid", "p-", "px-", "py-", "pt-", "pb-", "pl-", "pr-",
        "m-", "mx-", "my-", "mt-", "mb-", "ml-", "mr-", "w-", "h-", "min-", "max-",
        "rounded", "border", "shadow", "ring", "opacity", "overflow", "hidden", "block",
        "inline", "items-", "justify-", "gap-", "space-", "divide-", "sr-", "truncate",
        "whitespace-", "break-", "font-", "leading-", "tracking-", "underline",
        "no-underline", "italic", "not-italic", "uppercase", "lowercase", "capitalize",
        "cursor-", "pointer-", "select-", "resize-", "appearance-", "outline-",
        "transition", "duration-", "ease-", "animate-", "relative", "absolute",
        "fixed", "sticky", "static", "top-", "bottom-", "left-", "right-", "inset-",
        "z-", "col-", "row-", "order-", "grow", "shrink", "basis-", "object-",
        "aspect-", "container", "mx-auto", "table-", "align-", "list-", "decoration-",
        "indent-", "first-", "last-", "odd-", "even-", "line-clamp-", "backdrop-",
    )
    known_app_classes = frozenset({
        "multi-file-input",
        "selected-files-list",
        "material-section",
        "material-checkbox-row",
        "tab-btn",
        "tab-count",
        "tab-scroll",
        "tab-panel",
        "surface-card",
        "note-card",
        "table-scroll",
        "icon-btn",
        "tabs-header-desktop",
        "project-bottom-tabs",
        "project-bottom-tab",
        "project-bottom-tab-count",
        "checklist-toggle",
        "reply-btn",
        "quote-btn",
        "mention-item",
        "mention-dropdown",
        "hide-done-toggle",
        "material-filter",
        "material-search",
        "mine-toggle",
        "no-materials-results",
        "materials-grid",
        "materials-sections",
        "drag-over",
        "note-content",
    })

    errors = []
    for tmpl in (ROOT / "templates").rglob("*.html"):
        content = tmpl.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r'class=["\']([^"\']*)["\']', content):
            class_value = match.group(1)
            if "{%" in class_value or "{{" in class_value:
                continue
            for cls in class_value.split():
                base = cls
                while True:
                    stripped = re.sub(
                        r"^(?:sm:|md:|lg:|xl:|2xl:|hover:|focus:|active:|dark:|last:|first:|odd:|even:|file:)",
                        "",
                        base,
                    )
                    if stripped == base:
                        break
                    base = stripped
                if not re.match(r"^[\w:-]+$", base):
                    continue
                check_name = base[1:] if base.startswith("-") else base
                if any(check_name.startswith(p) for p in tailwind_prefixes):
                    continue
                if len(base) <= 1:
                    continue
                if base.startswith("ti"):
                    continue
                if base in known_app_classes:
                    continue
                if base not in defined:
                    errors.append(f"  {tmpl.relative_to(ROOT)}: .{base} not in style.css")
    return errors


def check_position_fixed_media_queries() -> list[str]:
    """Warn about position:fixed rules without media query hide."""
    style_css = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")
    errors = []
    for match in re.finditer(r"\.([\w-]+)\s*\{[^}]*position\s*:\s*fixed", style_css, re.DOTALL):
        cls = match.group(1)
        has_media = bool(re.search(
            rf"@media[^{{]+\{{\s*[^}}]*\.{re.escape(cls)}\s*\{{[^}}]*display\s*:\s*none",
            style_css, re.DOTALL
        ))
        if not has_media:
            errors.append(f"  .{cls} has position:fixed but no @media display:none override")
    return errors


def check_anchor_cards() -> list[str]:
    """Warn if <a> card containers lack display:block in style.css."""
    style_css = (ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")
    errors = []
    for tmpl in (ROOT / "templates").rglob("*.html"):
        content = tmpl.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r'<a\s[^>]*class=["\']([^"\']*)["\']', content):
            classes = match.group(1).split()
            card_classes = [c for c in classes if "card" in c.lower()]
            for card_cls in card_classes:
                pattern = rf"\.{re.escape(card_cls)}\s*\{{[^}}]*display\s*:\s*block"
                if not re.search(pattern, style_css, re.DOTALL):
                    errors.append(
                        f"  {tmpl.relative_to(ROOT)}: <a class='{card_cls}'> "
                        f"but .{card_cls} lacks display:block in style.css"
                    )
    return errors


def check_no_print_statements() -> list[str]:
    """Find print() calls in routers/ and utils/."""
    errors = []
    for directory in ["routers", "utils"]:
        for py_file in (ROOT / directory).rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(r"\bprint\s*\(", line) and not line.strip().startswith("#"):
                    errors.append(f"  {py_file.relative_to(ROOT)}:{i}: {line.strip()}")
    return errors


def check_no_jinja2templates_in_routers() -> list[str]:
    """Find Jinja2Templates instantiation in router files."""
    errors = []
    for py_file in (ROOT / "routers").rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        if "Jinja2Templates(" in content:
            errors.append(f"  {py_file.relative_to(ROOT)}: contains Jinja2Templates()")
    return errors


def check_no_redirect_response_isinstance() -> list[str]:
    """Find old auth pattern in routers."""
    errors = []
    for py_file in (ROOT / "routers").rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        if "isinstance(current_user" in content or "isinstance(user, RedirectResponse" in content:
            errors.append(f"  {py_file.relative_to(ROOT)}: old auth pattern detected")
    return errors


def check_python_syntax() -> list[str]:
    """Compile all .py files to check for syntax errors."""
    errors = []
    for py_file in ROOT.rglob("*.py"):
        if ".git" in str(py_file) or "__pycache__" in str(py_file):
            continue
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            errors.append(f"  {py_file.relative_to(ROOT)}: {result.stderr.strip()}")
    return errors


def check_http_endpoints(base_url: str = "http://localhost:8000") -> list[str]:
    """Basic HTTP smoke tests."""
    import urllib.request
    import urllib.error

    errors = []
    checks = [
        ("/health", [200], "health check"),
        ("/login",  [200], "login page"),
        ("/",       [200, 302], "root"),
    ]
    for path, expected_codes, description in checks:
        try:
            req = urllib.request.Request(f"{base_url}{path}", headers={"User-Agent": "smoke-test/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as exc:
            errors.append(f"  {description} ({path}): {exc}")
            continue
        if code not in expected_codes:
            errors.append(f"  {description} ({path}): got {code}, expected {expected_codes}")
    return errors


def run_all(include_http: bool = False) -> int:
    failures = 0
    sections = [
        ("Python syntax",                    check_python_syntax),
        ("No print() in routers/utils",      check_no_print_statements),
        ("No Jinja2Templates in routers",    check_no_jinja2templates_in_routers),
        ("No old auth isinstance pattern",   check_no_redirect_response_isinstance),
        ("CSS classes defined in style.css", check_css_classes),
        ("position:fixed has media query",   check_position_fixed_media_queries),
        ("<a> card has display:block",        check_anchor_cards),
    ]

    print("=" * 50)
    print("TeamSpace Smoke Tests")
    print("=" * 50)

    for title, check_fn in sections:
        errors = check_fn()
        if errors:
            print(f"\nFAIL: {title}")
            for e in errors[:10]:
                print(e)
            if len(errors) > 10:
                print(f"  ... и ещё {len(errors) - 10}")
            failures += 1
        else:
            print(f"OK:   {title}")

    if include_http:
        print("\n--- HTTP (localhost:8000) ---")
        http_errors = check_http_endpoints()
        if http_errors:
            print("FAIL: HTTP endpoints")
            for e in http_errors:
                print(e)
            failures += 1
        else:
            print("OK:   HTTP endpoints")

    print("\n" + "=" * 50)
    if failures:
        print(f"ИТОГО: {failures} проверок ПРОВАЛЕНО. Исправь перед коммитом.")
    else:
        print("ИТОГО: все проверки прошли. Можно коммитить.")
    return 1 if failures else 0


if __name__ == "__main__":
    include_http = "--http" in sys.argv
    sys.exit(run_all(include_http=include_http))
