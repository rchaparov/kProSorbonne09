## Task #002 — БД: SQLAlchemy модели + Alembic миграция

**Тип:** feat
**Приоритет:** Critical
**Зависит от:** Task #001

---

### Контекст

Полный слой данных. Все 6 таблиц в `database.py`.
Alembic генерирует первую миграцию `001_initial.py`.
Паттерн `init_database()` / `get_db_session()` — аналогично WKProxy.

---

### Acceptance Criteria

- [ ] `database.py` содержит все 6 моделей: `User`, `Session`, `Project`, `ProjectMember`, `Note`, `NoteAttachment`
- [ ] Функции `init_database(database_url)` и `get_db_session()` реализованы по образцу WKProxy
- [ ] `alembic.ini` настроен, `migrations/env.py` подключён к `database.py`
- [ ] Миграция `001_initial.py` создана и содержит все таблицы
- [ ] `system_role` — String: `admin`, `coordinator`, `member`
- [ ] `NoteAttachment.file_data` — тип `LargeBinary`
- [ ] `Project.status` — String: `active` | `completed`
- [ ] `ProjectMember` имеет `UniqueConstraint(project_id, user_id)`

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `database.py` |
| создать | `alembic.ini` |
| создать | `migrations/env.py` |
| создать | `migrations/script.py.mako` |
| создать | `migrations/versions/001_initial.py` |

---

### Технические детали

```python
class User(Base):
    __tablename__ = "users"
    id, username(unique), password_hash, full_name, business_role(nullable),
    system_role(default="member"), is_active(default=True), created_at

class Session(Base):
    __tablename__ = "sessions"
    id, user_id(FK->users), token(64, unique, index), expires_at, created_at

class Project(Base):
    __tablename__ = "projects"
    id, title, description(Text, nullable), deadline(DateTime, nullable),
    status(default="active"), created_by(FK->users), created_at, updated_at

class ProjectMember(Base):
    __tablename__ = "project_members"
    id, project_id(FK->projects), user_id(FK->users), joined_at
    UniqueConstraint(project_id, user_id)

class Note(Base):
    __tablename__ = "notes"
    id, project_id(FK->projects), author_id(FK->users), content(Text), created_at, updated_at

class NoteAttachment(Base):
    __tablename__ = "note_attachments"
    id, note_id(FK->notes, cascade delete), filename(String, UUID),
    original_filename, file_size(Integer), content_type, file_data(LargeBinary), uploaded_at
```

- Все FK с `ondelete="CASCADE"` там где логично
- В `migrations/env.py` импортировать `Base` из `database` → `target_metadata = Base.metadata`

---

### Проверка

- [ ] `python -c "from database import User, Project, Note, NoteAttachment, init_database"` — без ошибок
- [ ] `grep "op.create_table" migrations/versions/001_initial.py | wc -l` = 6

---

### Git

```bash
git add database.py alembic.ini migrations/
git commit -m "feat(db): SQLAlchemy models and Alembic initial migration"
```

---

### Ожидаю:

`database.py` импортируется. Миграция содержит все 6 таблиц.

Когда закончишь — напиши **"проверь"** и жди.
