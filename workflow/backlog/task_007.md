## Task #007 — Админ-панель: пользователи, проекты, назначения

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #005

---

### Контекст

Полная панель управления для роли `admin`.
Создание пользователей, проектов, назначение участников.
Все операции — HTML-формы (SSR, без AJAX).
Доступ: только `admin`. Остальные → 403.

---

### Acceptance Criteria

**Пользователи (`/admin/users`):**
- [ ] Список: full_name, username, business_role, system_role, статус, дата создания
- [ ] SVG иконки действий вместо текстовых кнопок (карандаш — редактировать, замок — пароль, переключатель — активировать/деактивировать)
- [ ] Форма создания: username, full_name, business_role (текст), system_role (select), password
- [ ] Форма редактирования: те же поля кроме password
- [ ] Смена пароля: `POST /admin/users/{id}/password`, одно поле `new_password`
- [ ] Toggle активности: `POST /admin/users/{id}/toggle`
- [ ] Дублирующийся username → форма с сообщением об ошибке, без краша

**Проекты (`/admin/projects`):**
- [ ] Список: title, deadline, status, кол-во участников
- [ ] SVG иконки: карандаш, архив (закрыть/открыть), группа людей (участники)
- [ ] Форма создания/редактирования: title, description (textarea), deadline (date input), status
- [ ] Toggle статуса: `POST /admin/projects/{id}/toggle` — active/completed
- [ ] Страница участников `/admin/projects/{id}/members`:
  - Текущие участники + кнопка удалить (SVG иконка корзины)
  - Select всех активных пользователей не состоящих в проекте + кнопка "Добавить"

**Общее:**
- [ ] Все роуты `/admin/*` защищены `Depends(require_admin)`
- [ ] `/admin/` — главная со ссылками на разделы
- [ ] Flash-сообщения через `?msg=...` query param (шаблон показывает если параметр есть)
- [ ] Навбар ссылка "Администрирование" ведёт на `/admin/`
- [ ] Никаких эмодзи — только SVG иконки

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `routers/admin.py` |
| создать | `templates/admin/index.html` |
| создать | `templates/admin/users.html` |
| создать | `templates/admin/user_form.html` |
| создать | `templates/admin/projects.html` |
| создать | `templates/admin/project_form.html` |
| создать | `templates/admin/project_members.html` |

---

### Технические детали

```python
router = APIRouter(prefix="/admin", tags=["admin"])

# Роуты:
GET  /admin/
GET  /admin/users
POST /admin/users                        # создать
GET  /admin/users/{user_id}/edit
POST /admin/users/{user_id}/edit         # обновить
POST /admin/users/{user_id}/toggle       # active/inactive
POST /admin/users/{user_id}/password     # сменить пароль
GET  /admin/projects
POST /admin/projects                     # создать
GET  /admin/projects/{project_id}/edit
POST /admin/projects/{project_id}/edit   # обновить
POST /admin/projects/{project_id}/toggle # active/completed
GET  /admin/projects/{project_id}/members
POST /admin/projects/{project_id}/members              # добавить участника
POST /admin/projects/{project_id}/members/{user_id}/remove  # удалить участника
```

**SVG иконки для действий:**
- Редактировать: `pencil-square` (Heroicons)
- Удалить/убрать: `trash`
- Участники: `user-group`
- Пароль: `key`
- Активировать: `check-circle`
- Деактивировать: `x-circle`
- Архив: `archive-box`

**business_role**: свободный текст — CEO, CTO, CDO, CIO, COO, CMO, CFO и др.
**system_role**: select из трёх значений: admin, coordinator, member.

**Валидация при создании:**
- username уникален — проверить в БД, вернуть форму с `?error=username_exists` при дубликате
- password минимум 6 символов

---

### Проверка

- [ ] `GET /admin/` с ролью coordinator → 403
- [ ] Создать пользователя → появляется в списке
- [ ] Дублирующийся username → форма с ошибкой
- [ ] Создать проект → появляется на дашборде
- [ ] Добавить участника → появляется на странице проекта
- [ ] Удалить участника → исчезает
- [ ] Сменить пароль → новый пароль работает при логине
- [ ] Нет эмодзи в шаблонах

---

### Git

```bash
git add routers/admin.py templates/admin/
git commit -m "feat(admin): user management, project management, member assignment"
```

---

### Ожидаю:

Полный цикл: создать пользователя → создать проект → назначить участника → проверить доступ.

Когда закончишь — напиши **"проверь"** и жди.
