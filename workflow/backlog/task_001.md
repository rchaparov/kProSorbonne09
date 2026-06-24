## Task #001 — Scaffold: структура проекта, конфиг, Railway

**Тип:** chore
**Приоритет:** Critical
**Зависит от:** нет зависимостей

---

### Контекст

Создаём скелет проекта TeamSpace с нуля.
Стек аналогичен WKProxy: FastAPI + SQLAlchemy + PostgreSQL + Alembic + Railway.

---

### Acceptance Criteria

- [ ] Файловая структура создана согласно дереву из ARCHITECT_ORCHESTRATOR_PROMPT.md
- [ ] `config.py` — Pydantic `BaseSettings`, читает из `.env`: `DATABASE_URL`, `SECRET_KEY`, `SESSION_LIFETIME_HOURS` (default 8), `MAX_UPLOAD_BYTES` (default 10485760), `PORT`
- [ ] `requirements.txt` содержит: `fastapi`, `uvicorn`, `gunicorn`, `jinja2`, `python-multipart`, `sqlalchemy==1.4.*`, `alembic`, `bcrypt`, `psycopg2-binary`, `pydantic==1.10.*`, `python-dotenv`, `aiofiles`
- [ ] `.env.example` — все переменные с плейсхолдерами, без реальных секретов
- [ ] `railway.toml` — builder nixpacks, startCommand через `$PORT`, healthcheck `/health`
- [ ] `Procfile` — gunicorn с uvicorn worker через `$PORT`
- [ ] `.gitignore` — `*.env`, `__pycache__`, `*.pyc`, `venv/`, `.pytest_cache/`
- [ ] Пустые `__init__.py` в `routers/`
- [ ] `validate_settings()` проверяет что `SECRET_KEY` не дефолтный и `DATABASE_URL` начинается с `postgresql://`

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `config.py` |
| создать | `requirements.txt` |
| создать | `.env.example` |
| создать | `railway.toml` |
| создать | `Procfile` |
| создать | `.gitignore` |
| создать | `routers/__init__.py` |
| создать | `static/css/style.css` (пустой) |

---

### Технические детали

- `DATABASE_URL` валидатор: заменяет `postgres://` на `postgresql://`
- `railway.toml` healthcheck path: `/health`
- `Procfile`: `web: gunicorn main:app -w ${WEB_CONCURRENCY:-2} -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

---

### Проверка

- [ ] `python -c "from config import settings; print(settings)"` — нет ошибок
- [ ] Все папки и файлы из структуры существуют
- [ ] `git status` не показывает `.env`

---

### Git

```bash
git init
git add .
git commit -m "chore(scaffold): project structure, config, railway deploy files"
```

---

### Ожидаю:

Файловый скелет готов, `config.py` импортируется без ошибок.

Когда закончишь — напиши **"проверь"** и жди.
