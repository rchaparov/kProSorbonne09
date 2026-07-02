## Task #028 — Бэкенд рефакторинг: auth паттерн, индексы, shared templates, DRY

**Тип:** refactor + chore
**Приоритет:** High
**Зависит от:** Task #027

---

### Контекст

Архитектурный долг выявленный при аудите. Нет изменений функциональности.

---

### Acceptance Criteria

**1. Исправить auth паттерн (Union[User, RedirectResponse] → HTTPException)**

Текущий антипаттерн: `get_current_user` возвращает `RedirectResponse` вместо исключения.
Каждый роутер делает `isinstance` проверки — потенциальный источник тихих багов.

Заменить на стандартный FastAPI паттерн:

```python
# auth.py — новый get_current_user
def get_current_user(
    request: Request,
    db: DbSession = Depends(get_db_session),
) -> User:
    """Resolve current user from session cookie or raise 302."""
    from fastapi.responses import RedirectResponse
    token = request.cookies.get("session_token")
    if not token:
        # Для HTML роутов — Response exception через специальный класс
        raise _RedirectException("/login")
    session = db.query(UserSession).filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        raise _RedirectException("/login")
    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or not user.is_active:
        raise _RedirectException("/login")
    return user
```

Добавить exception handler в `main.py`:
```python
class _RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url

@app.exception_handler(_RedirectException)
async def redirect_handler(request: Request, exc: _RedirectException):
    return RedirectResponse(exc.url, status_code=302)
```

После этого убрать все `isinstance(user, RedirectResponse)` проверки из всех роутеров.
Убрать бессмысленный `_require_user()` хелпер из `notes.py`.
Убрать `Union[User, RedirectResponse]` аннотации повсюду.

- [ ] `auth.py`: `get_current_user` возвращает `User` или поднимает `_RedirectException`
- [ ] `main.py`: обработчик `_RedirectException`
- [ ] Все роутеры: убраны `isinstance(current_user, RedirectResponse)` проверки
- [ ] `notes.py`: удалён `_require_user()`
- [ ] Тип `require_admin` и `require_coordinator_or_admin` тоже обновлены

**2. Shared Jinja2Templates**

- [ ] В `main.py` создать один глобальный `templates = Jinja2Templates(directory="templates")`
- [ ] Экспортировать: `from main import templates` в каждом роутере
- [ ] Удалить локальные `templates = Jinja2Templates(directory="templates")` из всех роутеров
- [ ] Роутеры: `admin.py`, `analytics.py`, `auth_router.py`, `checklist.py`, `dashboard.py`, `feed.py`, `files_temp.py`, `materials.py`, `notes.py`, `notifications.py`, `profile.py`, `projects.py`, `search.py`

**3. Индексы на горячих полях**

- [ ] Alembic миграция `009_performance_indexes.py`:
  ```python
  def upgrade():
      op.create_index("ix_notes_project_id", "notes", ["project_id"])
      op.create_index("ix_notes_parent_id", "notes", ["parent_id"])
      op.create_index("ix_notifications_user_id_is_read", "notifications",
                      ["user_id", "is_read"])
      op.create_index("ix_project_members_user_id", "project_members", ["user_id"])
      op.create_index("ix_checklist_items_project_id", "checklist_items", ["project_id"])
      op.create_index("ix_note_mentions_user_id", "note_mentions", ["user_id"])

  def downgrade():
      op.drop_index("ix_notes_project_id", "notes")
      op.drop_index("ix_notes_parent_id", "notes")
      op.drop_index("ix_notifications_user_id_is_read", "notifications")
      op.drop_index("ix_project_members_user_id", "project_members")
      op.drop_index("ix_checklist_items_project_id", "checklist_items")
      op.drop_index("ix_note_mentions_user_id", "note_mentions")
  ```

**4. N+1 в /analytics — один GROUP BY запрос**

- [ ] Заменить Python-цикл с двумя запросами на один:
  ```python
  from sqlalchemy import cast, Integer as SAInt

  checklist_totals = dict(
      db.query(ChecklistItem.project_id, func.count(ChecklistItem.id))
      .group_by(ChecklistItem.project_id).all()
  )
  checklist_dones = dict(
      db.query(ChecklistItem.project_id, func.count(ChecklistItem.id))
      .filter(ChecklistItem.is_done.is_(True))
      .group_by(ChecklistItem.project_id).all()
  )
  progresses = [
      project_progress(
          p.status,
          checklist_dones.get(p.id, 0),
          checklist_totals.get(p.id, 0),
      )
      for p in active_projects
  ]
  avg_progress = round(sum(progresses) / len(progresses)) if progresses else 0
  ```
  Два запроса вместо 2*N.

**5. Вынести `_parse_deadline` в utils**

- [ ] Добавить в `utils/date_utils.py`:
  ```python
  from datetime import datetime
  from typing import Optional

  def parse_deadline(value: Optional[str]) -> Optional[datetime]:
      if not value or not value.strip():
          return None
      try:
          return datetime.strptime(value.strip(), "%Y-%m-%d")
      except ValueError:
          return None
  ```
- [ ] Удалить `_parse_deadline` из `admin.py` и `checklist.py`
- [ ] Импортировать `parse_deadline` из `utils.date_utils`

**6. Исправить `admin_projects_toggle`**

- [ ] Текущая логика `active↔completed` ломает канбан с 5 статусами
- [ ] Заменить на переход `active → completed` и `completed → active` (те же 2 статуса для toggle кнопки)
- [ ] Для смены на planning/review/on_hold — использовать форму редактирования проекта
- [ ] Кнопку toggle переименовать в "Завершить" / "Вернуть в работу" для ясности

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| изменить | `auth.py` (_RedirectException, новый get_current_user) |
| изменить | `main.py` (exception handler, shared templates) |
| изменить | `routers/*.py` (все — убрать isinstance + локальные templates) |
| создать | `migrations/versions/009_performance_indexes.py` |
| создать | `utils/date_utils.py` |
| изменить | `routers/admin.py`, `routers/checklist.py` (use parse_deadline) |
| изменить | `routers/analytics.py` (N+1 fix) |

---

### Проверка

- [ ] `grep -r "isinstance(current_user, RedirectResponse)" routers/` — пустой вывод
- [ ] `grep -r "Jinja2Templates" routers/` — пустой вывод
- [ ] `grep -r "_require_user" routers/` — пустой вывод
- [ ] `grep -r "_parse_deadline" routers/` — пустой вывод
- [ ] Открыть `/analytics` — avg_progress вычисляется без N+1 (проверить Railway логи: один SQL на все проекты)
- [ ] Миграция 009 применяется: `alembic upgrade head`
- [ ] Неавторизованный пользователь → редиректится на `/login` (не 500)
- [ ] Все страницы открываются корректно

---

### Git

```bash
git add .
git commit -m "refactor(backend): proper auth pattern, shared templates, db indexes, N+1 fix, DRY utils"
```

---

### Ожидаю:

Нет `isinstance(RedirectResponse)` в роутерах. Один Templates инстанс. Индексы созданы. N+1 в analytics устранён.

Когда закончишь — напиши **"проверь"** и жди.
