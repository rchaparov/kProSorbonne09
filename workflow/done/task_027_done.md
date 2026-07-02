# Task #027 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Удалён DEBUG `print` из `routers/notes.py`
- Rate limit 5/min на `POST /profile/password` и `POST /admin/users/{id}/password`
- Авторизация вложений: `_can_access_note_attachment` для download/view
- Session invalidation при логине (удаление старых сессий)
- Redirect с `/login` для уже авторизованных пользователей
- `pool_pre_ping=True`, `pool_size=5`, `max_overflow=10` в `init_database()`
- `.strip()` на строковых Form полях в admin и materials

## Изменённые файлы
- `routers/notes.py` — удалён DEBUG, authz вложений
- `routers/profile.py` — rate limit
- `routers/admin.py` — rate limit, strip полей пользователя
- `routers/auth_router.py` — redirect если сессия валидна
- `auth.py` — инвалидация сессий при логине
- `database.py` — pool_pre_ping и pool settings
- `routers/materials.py` — strip title/description

## Обязательные проверки
- [x] `grep -r "print(" routers/ utils/` — пустой вывод: Да
- [ ] `grep -r "Jinja2Templates" routers/` — пустой вывод: Нет (существующий техдолг, не в scope)
- [x] `python -m py_compile main.py auth.py database.py routers/*` — без ошибок: Да
- [x] Alembic миграция проверена (если была): N/A

## Git
- commit hash: 0e07048
- branch: main
- push: ожидает "ПРИНЯТО"

## Замечания / Known issues
- `profile.py`: строковых Form полей кроме паролей нет — strip не применялся
