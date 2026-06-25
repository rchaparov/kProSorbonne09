# Task #013 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Локальное время: `<time data-utc>` + JS `toLocaleString('ru')` во всех указанных шаблонах
- `timeAgo()` для заметок и уведомлений (< 24 ч)
- Глобальный confirm перед удалением через `data-confirm` в `base.html`
- Мобильный navbar: burger-кнопка, dropdown-меню, имя и выход всегда видны

## Изменённые файлы
- `templates/base.html` — confirm JS, timeAgo, burger menu
- `templates/project_detail.html` — data-utc, data-timeago, data-confirm
- `templates/dashboard.html` — data-utc дедлайны
- `templates/notifications.html` — data-utc, data-timeago
- `templates/materials.html` — data-utc, data-confirm
- `templates/admin/users.html` — data-utc, data-confirm
- `templates/admin/projects.html` — data-utc, data-confirm
- `templates/admin/project_members.html` — data-confirm

## Git
- commit hash: 969f154
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: data-utc и data-confirm присутствуют во всех целевых шаблонах
- [x] Manual check: timeAgo и confirm JS в base.html
- [x] Manual check: burger-btn и nav-links в base.html
- [x] Manual check: emoji в шаблонах — не найдены

## Замечания / Known issues
нет
