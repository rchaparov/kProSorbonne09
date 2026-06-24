# Task #005 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `routers/dashboard.py` — GET `/` со списком всех проектов и подсчётом участников
- Создан `routers/projects.py` — GET `/projects/{id}` с участниками, лентой заметок и `can_write`
- Создан `templates/dashboard.html` — grid карточек проектов с SVG, бейджами дедлайна и статуса
- Создан `templates/project_detail.html` — детали проекта, участники, заметки, форма добавления по роли

## Изменённые файлы
- `routers/dashboard.py` — dashboard route
- `routers/projects.py` — project detail route
- `templates/dashboard.html` — список проектов
- `templates/project_detail.html` — страница проекта

## Git
- commit hash: 85c8edd
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: dashboard template рендерится с проектами
- [x] Manual check: `GET /projects/999` → HTTPException 404
- [x] Manual check: coordinator — `can_write=False`, форма не показывается
- [x] Manual check: member в проекте — `can_write=True`, форма видна
- [x] Manual check: member не в проекте — `can_write=False`, форма скрыта
- [x] Manual check: emoji в templates — не найдены

## Замечания / Known issues
нет
