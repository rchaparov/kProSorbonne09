# PROJECT STATUS — TeamSpace / kProSorbonne09
# Команда: Сорбона 09

**Последнее обновление:** старт проекта
**Текущая фаза:** Backlog готов, разработка не начата

---

## Статус задач

| # | Название | Статус |
|---|---|---|
| 001 | Scaffold: структура, config, railway files | Backlog |
| 002 | БД: SQLAlchemy модели + Alembic миграция | Backlog |
| 003 | Auth: сессии, cookie, зависимости ролей | Backlog |
| 004 | UI base: base.html, login.html, SVG иконки, auth router | Backlog |
| 005 | Dashboard + страница проекта (просмотр) | Backlog |
| 006 | Заметки + файловые вложения (upload/download) | Backlog |
| 007 | Админ-панель: пользователи, проекты, назначения | Backlog |
| 008 | Сборка main.py + Railway деплой | Backlog |

---

## Технический стек

- FastAPI + Jinja2 (SSR)
- PostgreSQL + SQLAlchemy 1.4 + Alembic
- Bcrypt + cookie sessions (8ч)
- Tailwind CSS CDN, SVG иконки, light theme
- Railway деплой

---

## Ключевые решения

- Файлы — bytea в PostgreSQL (max 10MB), без внешних сервисов
- Роли: admin / coordinator / member (system_role)
- business_role (CEO, CDO и др.) — текстовый лейбл, не влияет на права
- Member видит все проекты read-only; WRITE только в назначенных
- Никаких эмодзи в UI
