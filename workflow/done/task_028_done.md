# Task #028 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Auth паттерн: `_RedirectException` в `auth.py`, handler в `main.py`; `get_current_user` возвращает `User` или поднимает исключение
- Убраны `isinstance(current_user, RedirectResponse)`, `_require_user`, `Union[User, RedirectResponse]` из всех роутеров
- Shared templates: один `Jinja2Templates` в `main.py`, роутеры импортируют `from main import templates`
- Миграция `009_performance_indexes.py` — индексы на горячих полях
- N+1 fix в `/analytics`: два GROUP BY запроса вместо цикла по проектам
- `utils/date_utils.py` с `parse_deadline()`; удалён дублирующий `_parse_deadline` из admin/checklist
- Admin toggle проектов: только `active ↔ completed`, кнопки «Завершить» / «Вернуть в работу»

## Изменённые файлы
- `auth.py` — `_RedirectException`, новый `get_current_user`, HTTPException 403 в role deps
- `main.py` — shared templates, exception handler, импорт роутеров после templates
- `routers/*.py` — auth cleanup, shared templates import (HTML-роутеры)
- `utils/date_utils.py` — создан `parse_deadline()`
- `migrations/versions/009_performance_indexes.py` — индексы производительности
- `templates/admin/projects.html` — toggle только для active/completed

## Обязательные проверки
- [x] `grep -r "print(" routers/ utils/` — пустой вывод: Да
- [x] `grep -r "Jinja2Templates" routers/` — пустой вывод: Да
- [x] `grep -r "_require_user" routers/` — пустой вывод: Да
- [x] `grep -r "_parse_deadline" routers/` — пустой вывод: Да
- [x] `grep -r "isinstance(current_user, RedirectResponse)" routers/` — пустой вывод: Да
- [x] `python -m py_compile main.py auth.py database.py routers/*` — без ошибок: Да
- [ ] Alembic миграция проверена: N/A локально (009 создана, `alembic upgrade head` на Railway)

## Git
- commit hash: a815cc1
- branch: main
- push: ожидает "ПРИНЯТО"

## Замечания / Known issues
- `feed.py` и `files_temp.py` — JSON API, локальный `Jinja2Templates` не использовался; изменены только auth deps
- Циклический импорт `from main import templates` безопасен: templates создаётся до импорта роутеров
