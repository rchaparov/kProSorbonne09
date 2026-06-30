# Task #021 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Множественная загрузка файлов при создании заметки (`files`, max 5)
- `POST /notes/{id}/attachments` — тоже multiple, те же лимиты
- Валидация размера каждого файла с именем в ошибке
- JS-превью выбранных файлов под полем input

## Изменённые файлы
- `routers/notes.py` — helpers, create_note, upload_attachment
- `templates/project_detail.html` — multiple input, preview JS

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: 3 файла в одной заметке
- [ ] Manual check: 6 файлов → 400
- [ ] Manual check: oversized file → 413 с именем
- [x] Manual check: import main.py — OK

## Замечания / Known issues
нет
