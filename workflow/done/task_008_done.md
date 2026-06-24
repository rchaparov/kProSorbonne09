# Task #008 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `main.py` — сборка FastAPI-приложения TeamSpace
- Зарегистрированы все роутеры: auth, dashboard, projects, notes, admin
- Монтирована статика `/static`, startup вызывает только `init_database(settings.DATABASE_URL)`
- Обработчики ошибок: 404 → редирект на `/`, 403 → `templates/403.html`
- `validate_settings()` вызывается при импорте
- Обновлён `railway.toml` — `alembic upgrade head` в startCommand перед gunicorn

## Изменённые файлы
- `main.py` — точка входа приложения
- `railway.toml` — startCommand с миграциями

## Git
- commit hash: 5b82786
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: `from main import app` — без ошибок
- [x] Manual check: `GET /health` → `{"status": "ok"}`
- [x] Manual check: `GET /login` → HTML форма (200)
- [x] Manual check: обработчик 404 → редирект `/`
- [x] Manual check: обработчик 403 → страница «Доступ запрещён»

## Railway деплой
Railway CLI не авторизован в текущей сессии (`railway login` required). После push:
1. Railway → New Project → Deploy from GitHub → `rchaparov/kProSorbonne09`
2. Add Plugin → PostgreSQL
3. Variables: `SECRET_KEY`, `SESSION_LIFETIME_HOURS=8`, `MAX_UPLOAD_BYTES=10485760`
4. Проверить логи: `Running upgrade -> 001_initial`
5. `GET /health` на публичном URL

Пример `SECRET_KEY`: сгенерировать через `python -c "import secrets; print(secrets.token_urlsafe(48))"`

## Замечания / Known issues
- `alembic upgrade head` выполняется в startCommand (не в startup event), как указано в уточнении
- `configure_session_maker()` не используется — SessionLocal создаётся в `init_database()`
