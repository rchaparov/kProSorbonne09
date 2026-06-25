# Task #016 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Модель `TempFileToken` + миграция `005_temp_file_tokens.py`
- `POST /files/temp` — создание токена (TTL 5 мин) и `viewer_url` для Office Online
- `GET /files/temp/{token}` — публичная отдача файла (404/410)
- `BASE_URL` в `config.py`, очистка токенов при startup
- Кнопка «Просмотр» для Office-файлов в `materials.html` и `project_detail.html`
- `openOfficeViewer()` в `base.html`
- Исправлен 404 handler для `/files/*` (JSON вместо redirect)

## Изменённые файлы
- `database.py`, `config.py`, `.env.example`
- `migrations/versions/005_temp_file_tokens.py`
- `routers/files_temp.py`, `routers/materials.py`, `routers/projects.py`
- `main.py`, `templates/base.html`, `templates/materials.html`, `templates/project_detail.html`

## Git
- commit hash: beef7cc
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: POST /files/temp → viewer_url с officeapps.live.com
- [x] Manual check: GET /files/temp/{token} → 200 без auth
- [x] Manual check: bad token → 404, expired → 410
- [x] Manual check: BASE_URL пуст → POST 503
- [x] Manual check: import main.py — OK

## Замечания / Known issues
После деплоя добавить в Railway: `BASE_URL=https://sorbonne09-kpro.up.railway.app`
