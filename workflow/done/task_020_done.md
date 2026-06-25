# Task #020 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Миграция `008_checklist_deadline.py`, поле `deadline` в ChecklistItem
- GET/POST `/checklist/{id}/edit`, шаблон `checklist_edit.html`
- Дедлайн в форме добавления/редактирования, отображение в строке пункта
- 5 статусов проекта (канбан), бейджи на dashboard/project/admin
- `utils/progress.py` + прогресс-бар на дашборде и в шапке проекта
- opacity-60 для `completed` и `on_hold`

## Изменённые файлы
- `database.py`, `migrations/versions/008_checklist_deadline.py`
- `utils/progress.py`
- `routers/checklist.py`, `routers/dashboard.py`, `routers/projects.py`, `routers/admin.py`
- `templates/project_detail.html`, `templates/dashboard.html`
- `templates/admin/projects.html`, `templates/admin/project_form.html`
- `templates/checklist_edit.html`

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: редактирование пункта, дедлайн, статусы, прогресс
- [x] Manual check: project_progress formula — OK
- [x] Manual check: import main.py — OK

## Замечания / Known issues
нет
