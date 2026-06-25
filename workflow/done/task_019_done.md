# Task #019 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Левая колонка: чеклист сверху, участники снизу
- Таблица `checklist_item_assignees` + миграция `007` с переносом `assigned_to`
- Модель `ChecklistItemAssignee`, relationship `ChecklistItem.assignees`
- `POST /checklist` принимает несколько `assigned_to`, multiple select в форме
- Отображение всех ответственных через запятую

## Изменённые файлы
- `database.py` — ChecklistItemAssignee, убран assigned_to
- `migrations/versions/007_checklist_multi_assignees.py`
- `routers/checklist.py` — List[int] assigned_to
- `routers/projects.py` — joinedload assignees
- `templates/project_detail.html` — порядок блоков, multiple select, отображение

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: миграция 007, 2 ответственных на пункт
- [ ] Manual check: чеклист выше участников
- [x] Manual check: import main.py — OK

## Замечания / Known issues
нет
