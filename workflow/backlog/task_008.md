## Task #008 — Сборка main.py + Railway деплой

**Тип:** feat + chore
**Приоритет:** Critical
**Зависит от:** Task #007 (все предыдущие выполнены)

---

### Контекст

Финальная сборка: регистрируем все роутеры в `main.py`, подключаем статику и шаблоны,
startup event (alembic upgrade head), обработчики ошибок.
Деплой на Railway через GitHub push.

---

### Acceptance Criteria

**main.py:**
- [ ] Создаёт `FastAPI(title="TeamSpace", docs_url=None, redoc_url=None)`
- [ ] Монтирует `StaticFiles` на `/static`
- [ ] Jinja2Templates с папкой `templates` — глобальный объект, передаётся в роутеры
- [ ] Регистрирует все роутеры: auth_router, dashboard, projects, notes, admin
- [ ] `@app.on_event("startup")` — `init_database()` + `configure_session_maker()`
- [ ] Обработчик `404` → редирект на `/`
- [ ] Обработчик `403` → рендер `templates/403.html`
- [ ] `validate_settings()` вызывается до старта

**railway.toml startCommand:**
```
alembic upgrade head && gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```
(alembic upgrade в startCommand, не в startup event — надёжнее при деплое)

**Railway деплой:**
- [ ] Репозиторий запушен на GitHub
- [ ] Проект создан на Railway, GitHub repo подключён
- [ ] PostgreSQL addon добавлен (Railway автоматически пробрасывает `DATABASE_URL`)
- [ ] ENV variables в Railway: `SECRET_KEY` (сгенерировать: `python -c "import secrets; print(secrets.token_urlsafe(48))"`), `SESSION_LIFETIME_HOURS=8`, `MAX_UPLOAD_BYTES=10485760`
- [ ] Первый деплой: `alembic upgrade head` выполнился (видно в логах)
- [ ] `GET /health` на публичном URL → `{"status": "ok"}`
- [ ] Страница логина открывается

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `main.py` |
| обновить | `railway.toml` (startCommand с alembic) |

---

### Технические детали

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from config import settings, validate_settings
from database import init_database, configure_session_maker, get_session_maker
from routers.auth_router import router as auth_router
from routers.dashboard import router as dashboard_router
from routers.projects import router as projects_router
from routers.notes import router as notes_router
from routers.admin import router as admin_router

validate_settings()

app = FastAPI(title="TeamSpace", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(projects_router)
app.include_router(notes_router)
app.include_router(admin_router)

@app.on_event("startup")
async def startup():
    engine = init_database(settings.DATABASE_URL)
    session_maker = get_session_maker(engine)
    configure_session_maker(session_maker)

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return RedirectResponse("/")

@app.exception_handler(403)
async def forbidden(request: Request, exc):
    return templates.TemplateResponse("403.html", {"request": request}, status_code=403)
```

**Передача templates в роутеры:** создать `templates` в `main.py` и импортировать в роутеры,
либо каждый роутер создаёт свой `Jinja2Templates(directory="templates")` — оба варианта допустимы.

**Пошагово для Railway:**
1. `git push origin main`
2. Railway → New Project → Deploy from GitHub repo
3. Add Plugin → PostgreSQL
4. Variables → добавить `SECRET_KEY` и остальные
5. Дождаться деплоя → открыть публичный URL

---

### Проверка

- [ ] `uvicorn main:app --reload` локально → нет ошибок импорта
- [ ] `GET http://localhost:8000/health` → `{"status": "ok"}`
- [ ] Railway деплой: статус "Success" в логах
- [ ] Публичный URL Railway → страница логина
- [ ] В логах Railway: `Running upgrade -> 001_initial`
- [ ] Создать admin-пользователя напрямую в БД (или seed-скриптом), залогиниться, проверить полный флоу

---

### Git

```bash
git add main.py railway.toml
git commit -m "feat(main): app assembly, startup event, error handlers"
git push origin main
```

---

### Ожидаю:

TeamSpace запущен на Railway. Страница логина открывается по публичному URL.

Когда закончишь — напиши **"проверь"** и жди.
