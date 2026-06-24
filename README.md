# TeamSpace — kProSorbonne09
# Команда: Сорбона 09

Внутреннее рабочее пространство команды для совместной работы над проектами в период обучения.

## Стек

- FastAPI + Jinja2 (SSR)
- PostgreSQL + SQLAlchemy + Alembic
- Bcrypt + cookie sessions
- Tailwind CSS CDN
- Railway деплой

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env
# Заполнить .env
alembic upgrade head
uvicorn main:app --reload
```

## Управление задачами

Смотри `workflow/` — там полный backlog и инструкции для агентов.
