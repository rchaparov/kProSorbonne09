## Task #004 — UI base: base.html, login.html, SVG иконки, auth router

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #003

---

### Контекст

Базовый UI-фундамент. Все шаблоны наследуют `base.html`.
Логин и логаут — первое что видит пользователь.
Тема: light. Tailwind CSS через CDN. Иконки — только SVG (inline или спрайт).

---

### Acceptance Criteria

- [ ] `templates/base.html` — layout с navbar, блоки `title`, `content`
- [ ] Navbar: имя пользователя, business_role (лейбл), SVG иконка выхода + кнопка "Выйти"
- [ ] Navbar для `admin`: ссылка "Администрирование" с SVG иконкой
- [ ] `templates/login.html` — форма: username + password, кнопка "Войти", flash-ошибка
- [ ] `templates/403.html` — страница "Доступ запрещён" с кнопкой "На главную"
- [ ] `routers/auth_router.py`: `GET /login`, `POST /login`, `POST /logout`, `GET /health`
- [ ] После успешного логина → редирект на `/`
- [ ] После логаута → cookie очищается, редирект на `/login`
- [ ] При неверных credentials → `GET /login?error=1` + сообщение об ошибке в шаблоне
- [ ] `GET /health` → `{"status": "ok"}`
- [ ] Никаких эмодзи в шаблонах — только SVG иконки

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `templates/base.html` |
| создать | `templates/login.html` |
| создать | `templates/403.html` |
| создать | `routers/auth_router.py` |
| изменить | `static/css/style.css` |

---

### Технические детали

**Дизайн (light theme):**
- Фон страницы: `bg-gray-50`
- Карточки: `bg-white shadow rounded-lg`
- Navbar: белый, `border-b border-gray-200`
- Акцентный цвет: `indigo-600`
- Tailwind CDN: `<script src="https://cdn.tailwindcss.com"></script>`

**SVG иконки** — использовать Heroicons (inline SVG, MIT лицензия):
- Выход: `arrow-right-on-rectangle` (logout)
- Администрирование: `cog-6-tooth` (settings)
- Пользователь: `user-circle`
- Проект: `folder`
- Заметка: `document-text`
- Скрепка/вложение: `paper-clip`
- Скачать: `arrow-down-tray`
- Удалить: `trash`
- Добавить: `plus`
Источник иконок: https://heroicons.com/ (вставлять inline SVG, 20x20 или 24x24)

**auth_router.py:**
```python
router = APIRouter(tags=["auth"])

@router.get("/login")
async def login_page(request: Request, error: str = None): ...

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)): ...

@router.post("/logout")
async def logout(request: Request): ...

@router.get("/health")
async def health(): return {"status": "ok"}
```

**base.html:** переменные `current_user` и `request` — всегда передаются из роутеров.

---

### Проверка

- [ ] `GET /login` — возвращает HTML форму без ошибок рендера
- [ ] `GET /health` — `{"status": "ok"}`
- [ ] `POST /login` с неверными данными → `/login?error=1` с сообщением
- [ ] Нет ни одного эмодзи в шаблонах (`grep -r "emoji\|&#x" templates/` — пусто)
- [ ] SVG иконки отображаются корректно

---

### Git

```bash
git add templates/ routers/auth_router.py static/
git commit -m "feat(ui): base layout, login, SVG icons, auth router, health endpoint"
```

---

### Ожидаю:

Страница логина открывается. SVG иконки видны. `/health` отвечает.

Когда закончишь — напиши **"проверь"** и жди.
