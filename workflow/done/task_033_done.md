# Task #033 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Фикс метрики дедлайна: завершённые проекты показывают «Сдан {дата}» / «Завершён», без «просрочен»
- Страница проекта переведена на вкладки: Обсуждение, Чеклист, Материалы, Аналитика, Участники
- Hash-пersistence (#notes, #checklist, …), polling заметок только на вкладке Обсуждение
- Удалена sticky якорная навигация section-nav-link
- Redirect после заметок/чеклиста с hash вкладки
- Запрос `project_materials` для вкладки Материалы

## Изменённые файлы
- `routers/projects.py` — project_materials, убран deadline_days_label
- `routers/notes.py` — redirect `#notes`
- `routers/checklist.py` — redirect `#checklist`
- `templates/project_detail.html` — вкладки, фикс дедлайна, участники с аватарами
- `static/css/style.css` — стили tab-btn, tab-count, tab-scroll
- `tests/smoke_test.py` — known_app_classes для вкладок

## Результаты обязательного чеклиста
- [x] python -m py_compile — без ошибок: Да
- [x] python tests/smoke_test.py — все OK: Да (7/7)
- [x] Завершённый проект — зелёный «Сдан», не просрочен: Да (шаблон)
- [x] Вкладки + hash: Да
- [x] Polling guard: Да
- [x] section-nav-link удалён: Да

## Git
- commit hash: c097a4c
- push: ожидает «ПРИНЯТО»

## Замечания
- Пагинация заметок сохраняет `#notes` в URL
