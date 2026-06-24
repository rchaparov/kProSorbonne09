# Task #009 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `routers/profile.py` — GET `/profile`, POST `/profile/password` с валидацией
- Создан `templates/profile.html` — read-only данные аккаунта и форма смены пароля
- Добавлен `GET /attachments/{id}/view` — inline для PDF и image/*, attachment для остальных
- Обновлён `project_detail.html` — кнопка «Открыть» (SVG eye) рядом со скачиванием
- Обновлён `base.html` — ссылка на `/profile` в navbar
- Подключён profile router в `main.py`

## Изменённые файлы
- `routers/profile.py` — профиль и смена пароля
- `templates/profile.html` — страница профиля
- `routers/notes.py` — inline-просмотр вложений
- `templates/project_detail.html` — кнопка «Открыть»
- `templates/base.html` — ссылка «Профиль»
- `main.py` — регистрация profile router

## Git
- commit hash: 84f7cf5
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: смена пароля — wrong_password, too_short, mismatch, changed
- [x] Manual check: `_attachment_disposition` — PDF/PNG inline, docx attachment
- [x] Manual check: `view_attachment` — inline/attachment headers
- [x] Manual check: emoji в profile.html — не найдены

## Замечания / Known issues
нет
