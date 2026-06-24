# Task #006 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `routers/notes.py` — CRUD заметок и вложений с проверкой прав
- POST `/projects/{id}/notes` — создание заметки с редиректом
- POST `/notes/{id}/delete` и DELETE `/notes/{id}` — удаление заметки (автор или admin)
- POST `/notes/{id}/attachments` — загрузка файла с лимитом MAX_UPLOAD_BYTES
- GET `/attachments/{id}/download` — скачивание с Content-Disposition
- POST `/attachments/{id}/delete` и DELETE `/attachments/{id}` — удаление вложения
- Обновлён `project_detail.html` — формы upload, кнопки удаления, иконка скачивания

## Изменённые файлы
- `routers/notes.py` — маршруты заметок и вложений
- `templates/project_detail.html` — формы upload/delete, SVG иконки

## Git
- commit hash: 5f75cdd
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: создание заметки — OK, редирект на проект
- [x] Manual check: загрузка файла — attachment сохраняется
- [x] Manual check: файл > 10MB → HTTP 413
- [x] Manual check: скачивание — правильное имя и content
- [x] Manual check: coordinator → 403 при создании заметки
- [x] Manual check: member не в проекте → 403
- [x] Manual check: удаление вложения и заметки — OK
- [x] Manual check: emoji в шаблоне — не найдены

## Замечания / Known issues
нет
