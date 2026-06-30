# Task #024 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Breadcrumbs на project_detail, checklist_edit, note_edit, materials, analytics, admin/*
- В navbar рядом с логотипом — выпадающий список «Проекты» (8 последних по updated_at)
- Текущий проект подсвечен; закрытие по клику вне / Escape
- Ссылка «Все проекты →» на дашборд
- Хелпер `utils/nav.py`: `get_recent_projects`, `nav_context`

## Изменённые файлы
- `utils/nav.py` — новый
- `templates/base.html` — dropdown, breadcrumbs block, JS
- `templates/project_detail.html`, `checklist_edit.html`, `note_edit.html`, `materials.html`, `analytics.html`
- `templates/admin/*.html` — breadcrumbs
- `routers/dashboard.py`, `projects.py`, `checklist.py`, `notes.py`, `materials.py`, `analytics.py`, `admin.py`, `notifications.py`, `search.py`, `profile.py`

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: breadcrumbs на всех страницах из AC
- [ ] Manual check: dropdown проектов, подсветка текущего
- [ ] Manual check: member vs admin/coordinator в списке
- [x] Import check: `utils.nav` — OK

## Замечания / Known issues
нет
