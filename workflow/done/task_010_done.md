# Task #010 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Добавлены модели `NoteMention` и `Notification` + миграция `002_mentions_notifications.py`
- `POST /projects/{id}/notes` — опциональный файл и mentions при создании заметки
- Уведомления для отмеченных участников (кроме автора)
- `routers/notifications.py` — `/notifications`, read-all, read-one с редиректом на проект
- `get_unread_count()` в `auth.py`, колокольчик в navbar
- Форма заметки: чекбоксы участников, файл, бейджи mentions в ленте

## Изменённые файлы
- `database.py` — модели NoteMention, Notification
- `migrations/versions/002_mentions_notifications.py` — новая миграция
- `auth.py` — get_unread_count
- `routers/notes.py` — create_note с файлом и mentions, view route
- `routers/notifications.py` — страница уведомлений
- `routers/projects.py` — mentions в note_items, unread_count
- `routers/dashboard.py`, `profile.py`, `auth_router.py`, `admin.py` — unread_count
- `templates/notifications.html` — список уведомлений
- `templates/project_detail.html` — форма и бейджи
- `templates/base.html` — колокольчик
- `main.py` — notifications router

## Git
- commit hash: 8f91281
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: заметка с файлом и mention — attachment + notification созданы
- [x] Manual check: автор не получает уведомление о себе
- [x] Manual check: get_unread_count для упомянутого пользователя = 1
- [x] Manual check: миграция 002 содержит 2 таблицы
- [x] Manual check: import main.py — OK
- [x] Manual check: emoji в notifications.html — не найдены

## Замечания / Known issues
нет
