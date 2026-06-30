# Task #026 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- `utils/uploads.py` — общая валидация множественных файлов
- `routers/notes.py` — рефакторинг на `read_validated_files` (поведение без изменений)
- Материалы: multi-file create, add files, edit, mine filter, usage count
- Client-side поиск на странице материалов и в форме заметки

## Изменённые файлы
- `utils/uploads.py` — новый
- `routers/notes.py`, `routers/materials.py`
- `templates/materials.html`, `material_form.html`, `material_edit.html`, `project_detail.html`

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Import check — OK
- [ ] Manual check: multi-file, edit, search, mine, usage count

## Замечания / Known issues
нет
