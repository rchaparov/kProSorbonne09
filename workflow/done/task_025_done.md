# Task #025 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Мобильный порядок: заметки (order-1) перед чеклистом/участниками (order-2)
- Sticky якорная панель: Чеклист / Участники / Заметки со счётчиками
- Кнопка «наверх» после скролла > 600px
- Client-side фильтр «Скрыть выполненные» для чеклиста
- Пагинация заметок с номерами страниц и «…»

## Изменённые файлы
- `utils/pagination.py` — новый
- `routers/projects.py` — `page_numbers` в контекст
- `templates/project_detail.html` — layout, nav, JS, пагинация

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] `paginate_range(5, 10)` — OK
- [ ] Manual check: mobile order, anchor nav, scroll-top, checklist filter

## Замечания / Known issues
нет
