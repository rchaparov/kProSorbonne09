# Task #035 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Убран мёртвый if/else в `analytics.py` при заполнении `status_counts`
- Спарклайн: один GROUP BY вместо 14 COUNT-запросов; общий хелпер `_sparkline_notes` в `utils/analytics_helpers.py`
- Cache-busting: `static_version` из `RAILWAY_GIT_COMMIT_SHA` (или timestamp) в Jinja globals, `?v=` на `style.css`

## Изменённые файлы
- `utils/analytics_helpers.py` — новый хелпер спарклайна
- `routers/analytics.py` — dead code, импорт хелпера
- `routers/projects.py` — импорт хелпера вместо цикла
- `main.py` — `STATIC_VERSION`, `templates.env.globals`
- `templates/base.html` — `style.css?v={{ static_version }}`

## Результаты обязательного чеклиста
- [x] python -m py_compile — без ошибок: Да
- [x] grep `if status in status_counts` routers/analytics.py — пустой: Да
- [x] python tests/smoke_test.py — все OK: Да (7/7)

## Git
- commit hash: PENDING
- push: ожидает «ПРИНЯТО»

## Замечания
- Логика спарклайна: 14 дней через `cast(Note.created_at, Date)` + GROUP BY; дни без заметок — count 0
