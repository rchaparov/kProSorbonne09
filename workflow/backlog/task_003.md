## Task #003 — Auth: сессии, cookie, зависимости ролей

**Тип:** feat
**Приоритет:** Critical
**Зависит от:** Task #002

---

### Контекст

Весь слой авторизации. Cookie-based сессии (без JWT).
Три зависимости FastAPI для проверки ролей — используются во всех роутерах.
Хелперы: bcrypt, генерация токенов.

---

### Acceptance Criteria

- [ ] `auth.py` содержит `login_user(username, password, db)` — создаёт Session, возвращает token
- [ ] `auth.py` содержит `get_current_user(request, db)` — читает cookie `session_token`, проверяет `expires_at`, возвращает `User` или редирект на `/login`
- [ ] Три зависимости: `require_admin(user)`, `require_coordinator_or_admin(user)`, `require_authenticated(user)` — raise `HTTPException(403)` при несоответствии
- [ ] `logout_user(token, db)` — удаляет Session из БД
- [ ] `hash_password(plain)`, `verify_password(plain, hashed)` — через bcrypt
- [ ] `generate_token(n=64)` — через `secrets.token_urlsafe(n)`
- [ ] `can_write_to_project(project_id, user, db) -> bool` — True если admin или в project_members

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `auth.py` |

---

### Технические детали

```python
def get_current_user(request: Request, db: Session = Depends(get_db_session)) -> User:
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    session = db.query(Session).filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        return RedirectResponse("/login", status_code=302)
    user = db.query(User).filter_by(id=session.user_id).first()
    if not user or not user.is_active:
        return RedirectResponse("/login", status_code=302)
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.system_role != "admin":
        raise HTTPException(403, "Forbidden")
    return user

def can_write_to_project(project_id: int, user: User, db) -> bool:
    if user.system_role == "admin":
        return True
    return db.query(ProjectMember).filter_by(
        project_id=project_id, user_id=user.id
    ).first() is not None
```

- Срок сессии: `settings.SESSION_LIFETIME_HOURS` (default 8)
- Cookie: `httponly=True`, `samesite="lax"`

---

### Проверка

- [ ] `python -c "from auth import get_current_user, require_admin, hash_password, verify_password, generate_token; print('OK')"` — без ошибок
- [ ] `verify_password("test", hash_password("test"))` -> True
- [ ] `verify_password("wrong", hash_password("test"))` -> False

---

### Git

```bash
git add auth.py
git commit -m "feat(auth): cookie sessions, role dependencies, bcrypt helpers"
```

---

### Ожидаю:

`auth.py` импортируется без ошибок. Bcrypt хелперы работают.

Когда закончишь — напиши **"проверь"** и жди.
