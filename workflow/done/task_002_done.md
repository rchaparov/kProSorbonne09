# Task #002 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `database.py` с 6 моделями: `User`, `Session`, `Project`, `ProjectMember`, `Note`, `NoteAttachment`
- Реализованы `init_database(database_url)` и `get_db_session()` (generator для request-scoped сессий)
- Настроены `alembic.ini` и `migrations/env.py` с `target_metadata = Base.metadata`
- Создана миграция `001_initial.py` с 6 таблицами и FK CASCADE

## Изменённые файлы
- `database.py` — модели SQLAlchemy 1.4, инициализация engine/session
- `alembic.ini` — конфиг Alembic
- `migrations/env.py` — подключение к `database.Base` и `config.settings`
- `migrations/script.py.mako` — шаблон миграций
- `migrations/versions/001_initial.py` — начальная схема БД

## Git
- commit hash: 6bf3e34
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: `py -3 -c "from database import User, Project, Note, NoteAttachment, init_database"` — без ошибок
- [x] Manual check: `op.create_table` в `001_initial.py` — 6 таблиц

## Замечания / Known issues
нет
