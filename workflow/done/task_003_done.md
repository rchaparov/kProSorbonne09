# Task #003 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Создан `auth.py` с cookie-based сессиями и bcrypt-хелперами
- Реализованы `login_user`, `logout_user`, `get_current_user` с редиректом на `/login`
- Добавлены зависимости `require_authenticated`, `require_admin`, `require_coordinator_or_admin`
- Реализован `can_write_to_project` для проверки прав записи в проект

## Изменённые файлы
- `auth.py` — авторизация, сессии, роли, bcrypt, генерация токенов

## Git
- commit hash: 90fbc85
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [x] Manual check: импорт `get_current_user`, `require_admin`, `hash_password`, `verify_password`, `generate_token` — OK
- [x] Manual check: `verify_password("test", hash_password("test"))` → True
- [x] Manual check: `verify_password("wrong", hash_password("test"))` → False

## Замечания / Known issues
нет
