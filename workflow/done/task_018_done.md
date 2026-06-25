# Task #018 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- `GET /projects/{id}/notes/feed` — JSON новых корневых заметок и replies после timestamp
- Polling каждые 20 сек на странице 1, баннер «Новые заметки (N)», reload по клику
- `data-last-seen` на контейнере ленты, polling пауза при скрытой вкладке
- Фикс @mention: `Form(None)` + нормализация single int, submit listener для hidden inputs
- DEBUG-лог `mentions` в stderr при создании заметки

## Изменённые файлы
- `routers/feed.py` — новый endpoint polling
- `routers/notes.py` — фикс парсинга mentions, debug log
- `routers/projects.py` — `last_seen_at` в контекст
- `templates/project_detail.html` — баннер, notes-feed, polling JS, submit listener
- `main.py` — подключение feed router

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: feed endpoint возвращает JSON
- [ ] Manual check: баннер через 20 сек при новой заметке
- [ ] Manual check: @mention сохраняется, бейдж виден
- [x] Manual check: import main.py — OK

## Замечания / Known issues
нет
