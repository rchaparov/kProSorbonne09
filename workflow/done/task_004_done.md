# Task #004 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `templates/base.html` — layout с navbar, блоками title/content, SVG-иконками Heroicons
- Создан `templates/login.html` — форма входа с flash-ошибкой
- Создан `templates/403.html` — страница «Доступ запрещён»
- Создан `routers/auth_router.py` — GET/POST `/login`, POST `/logout`, GET `/health`
- Обновлён `static/css/style.css` — базовые стили

## Изменённые файлы
- `templates/base.html` — navbar, user info, admin link, logout
- `templates/login.html` — форма username/password
- `templates/403.html` — forbidden page
- `routers/auth_router.py` — auth routes + health endpoint
- `static/css/style.css` — typography и focus styles

## Git
- commit hash: df45cff
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: `GET /login` — HTML форма рендерится
- [x] Manual check: `GET /health` — `{"status": "ok"}`
- [x] Manual check: `login_user('bad', 'bad', db)` → None, редирект на `/login?error=1`
- [x] Manual check: `grep emoji/&#x` в templates — пусто
- [x] Manual check: SVG иконки в base.html (user-circle, cog-6-tooth, arrow-right-on-rectangle)

## Замечания / Known issues
нет
