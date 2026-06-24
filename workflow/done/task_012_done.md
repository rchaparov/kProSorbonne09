# Task #012 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Убраны чекбоксы участников из формы заметки
- Inline @mention dropdown в textarea (vanilla JS)
- Фильтрация по символам после `@`, `@all` в первой позиции
- Выбор кликом или Enter — вставка `@full_name`, hidden input `mentions`
- Дедупликация hidden inputs по user_id
- `@all` добавляет hidden inputs для всех участников
- Закрытие по Escape и клику вне dropdown
- Позиционирование dropdown под курсором с учётом границ экрана
- `members_json` в контексте `projects.py`

## Изменённые файлы
- `templates/project_detail.html` — форма, dropdown JS
- `routers/projects.py` — members_json в контексте

## Git
- commit hash: 98a88fb
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: import main.py — OK
- [x] Manual check: чекбоксы убраны из шаблона
- [x] Manual check: emoji в project_detail.html — не найдены
- [x] Manual check: members_json передаётся в шаблон

## Замечания / Known issues
нет
