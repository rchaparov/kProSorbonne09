# Task #007 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `routers/admin.py` — полная админ-панель с защитой `require_admin`
- CRUD пользователей: список, создание, редактирование, toggle активности, смена пароля
- CRUD проектов: список, создание, редактирование, toggle статуса active/completed
- Управление участниками проекта: добавление и удаление
- Flash-сообщения через `?msg=` и ошибки через `?error=`
- SVG-иконки Heroicons для всех действий
- Обновлена ссылка «Администрирование» в navbar → `/admin/`

## Изменённые файлы
- `routers/admin.py` — все `/admin/*` маршруты
- `templates/admin/index.html` — главная админ-панели
- `templates/admin/users.html` — список и создание пользователей
- `templates/admin/user_form.html` — редактирование пользователя
- `templates/admin/projects.html` — список и создание проектов
- `templates/admin/project_form.html` — редактирование проекта
- `templates/admin/project_members.html` — управление участниками
- `templates/base.html` — ссылка на `/admin/`

## Git
- commit hash: 7290d5c
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: coordinator → HTTP 403 через `require_admin`
- [x] Manual check: создание пользователя — OK
- [x] Manual check: дублирующийся username → `error=username_exists`
- [x] Manual check: создание проекта — OK
- [x] Manual check: добавление/удаление участника — OK
- [x] Manual check: смена пароля — verify_password OK
- [x] Manual check: emoji в шаблонах admin — не найдены

## Замечания / Known issues
нет
