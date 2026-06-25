# Task #014 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- SQLAlchemy relationships + joinedload в projects, materials, admin
- Очистка просроченных сессий при startup
- Rate limit 5/min на POST /login (slowapi) + 429 → login.html
- GET /search — поиск по проектам, заметкам, материалам
- GET/POST /notes/{id}/edit — редактирование заметки (автор/admin)
- GET /health с проверкой БД (503 при недоступности)
- Поле поиска в navbar, шаблоны search.html и note_edit.html

## Изменённые файлы
- `database.py` — relationships для joinedload
- `limiter.py` — slowapi limiter
- `main.py` — startup cleanup, rate limit handler, search router
- `requirements.txt` — slowapi
- `routers/projects.py`, `materials.py`, `admin.py`, `notes.py`, `auth_router.py`
- `routers/search.py` — новый роутер
- `templates/base.html`, `search.html`, `note_edit.html`, `project_detail.html`, `login.html`

## Git
- commit hash: b500e4b
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: import main.py — OK
- [x] Manual check: GET /health → db ok
- [x] Manual check: GET /search?q=mvp — находит проект и заметку
- [x] Manual check: GET /search?q=a — подсказка 2 символа
- [x] Manual check: edit note — content обновлён, updated_at изменён
- [x] Manual check: member GET /notes/{id}/edit → 403
- [x] Manual check: 6 POST /login → 429

## Замечания / Known issues
нет
