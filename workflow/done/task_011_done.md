# Task #011 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Добавлены модели `Material` и `MaterialFile` + миграция `003_materials.py`
- Раздел `/materials` — список по категориям, фильтр таблетками, карточки с SVG-иконками
- `GET/POST /materials/new` — форма добавления (текст, URL, файл)
- Скачивание и inline-просмотр файлов материалов (PDF, изображения)
- `POST /materials/{id}/delete` — только автор или admin
- Ссылка «Материалы» в navbar
- Переименование сайта на «K-PRO Sorbonne 09 TeamSpace» во всех шаблонах и в FastAPI title

## Изменённые файлы
- `database.py` — MATERIAL_CATEGORIES, Material, MaterialFile
- `migrations/versions/003_materials.py` — новая миграция
- `routers/materials.py` — CRUD материалов, файлы
- `templates/materials.html`, `templates/material_form.html` — UI раздела
- `templates/base.html` — navbar, бренд, title
- `templates/login.html`, `dashboard.html`, `profile.html`, `notifications.html`, `403.html`, `project_detail.html`, `admin/index.html` — title/heading
- `main.py` — materials router, app title

## Git
- commit hash: 5b9c2d3
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: материал только с текстом — сохраняется
- [x] Manual check: материал с URL — url сохранён
- [x] Manual check: материал с файлом — MaterialFile создан, inline view для PDF
- [x] Manual check: удаление admin — OK
- [x] Manual check: миграция 003 содержит 2 create_table
- [x] Manual check: import main.py — OK
- [x] Manual check: emoji в шаблонах — не найдены

## Замечания / Known issues
нет
