# Task #015 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Модели `ChecklistItem`, `NoteMaterialLink` + миграция `004_checklist_note_materials.py`
- Роутер `checklist.py`: добавление, toggle, удаление пунктов
- Блок чеклиста на странице проекта (счётчик, назначение, read-only для coordinator)
- Прикрепление материалов к заметкам через `material_ids` и `NoteMaterialLink`
- Секция «Материалы» в ленте заметок, коллапс в форме создания
- Якорь `id="material-{id}"` на карточках материалов

## Изменённые файлы
- `database.py` — ChecklistItem, NoteMaterialLink, relationships
- `migrations/versions/004_checklist_note_materials.py`
- `routers/checklist.py`, `notes.py`, `projects.py`
- `templates/project_detail.html`, `materials.html`
- `main.py`

## Git
- commit hash: f7c1c9b
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: checklist add/toggle — OK
- [x] Manual check: note with 2 material_ids → 2 links (dedup)
- [x] Manual check: coordinator — checklist без формы добавления
- [x] Manual check: import main.py — OK
- [x] Manual check: миграция 004 — 2 create_table

## Замечания / Known issues
нет
