## Task #005 — Dashboard + страница проекта (просмотр)

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #004

---

### Контекст

Две главные страницы чтения: список всех проектов и детальная страница проекта.
Все роли видят все проекты (read-only).
Member в своих проектах видит кнопки добавления заметки.

---

### Acceptance Criteria

**Dashboard (`GET /`):**
- [ ] Показывает все проекты для всех ролей
- [ ] Карточка проекта: заголовок, описание (обрезанное до 100 символов), дедлайн, статус, кол-во участников
- [ ] Дедлайн просрочен → красный бейдж; активен → зелёный; нет дедлайна → бейдж не показывается
- [ ] Статус `completed` → карточка визуально приглушена (`opacity-60` или серый фон)
- [ ] SVG иконка папки на карточке проекта
- [ ] Клик на карточку → `/projects/{id}`

**Страница проекта (`GET /projects/{id}`):**
- [ ] Заголовок, описание, дедлайн, статус, дата создания
- [ ] Блок "Участники": full_name + business_role, SVG иконка пользователя
- [ ] Лента заметок (новые сверху): автор, дата, содержимое, список вложений
- [ ] Вложения: SVG иконка скрепки + `original_filename` + ссылка `/attachments/{id}/download`
- [ ] Если `can_write` → форма "Добавить заметку" (textarea + кнопка с SVG иконкой плюса)
- [ ] Если не `can_write` → форм нет
- [ ] `GET /projects/999` → 404

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `routers/dashboard.py` |
| создать | `routers/projects.py` |
| создать | `templates/dashboard.html` |
| создать | `templates/project_detail.html` |

---

### Технические детали

```python
# routers/dashboard.py
@router.get("/")
async def dashboard(request: Request,
                    current_user=Depends(get_current_user),
                    db=Depends(get_db_session)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    # Для каждого проекта считаем кол-во участников через subquery или len()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "current_user": current_user, "projects": projects
    })

# routers/projects.py
@router.get("/projects/{project_id}")
async def project_detail(project_id: int, request: Request,
                          current_user=Depends(get_current_user),
                          db=Depends(get_db_session)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(404)
    notes = db.query(Note).filter_by(project_id=project_id)\
               .order_by(Note.created_at.desc()).all()
    members = db.query(ProjectMember).filter_by(project_id=project_id).all()
    can_write = can_write_to_project(project_id, current_user, db)
    return templates.TemplateResponse("project_detail.html", {
        "request": request, "current_user": current_user,
        "project": project, "notes": notes,
        "members": members, "can_write": can_write
    })
```

**UI:**
- Dashboard: grid 3 колонки на desktop, 1 на mobile (`grid-cols-1 md:grid-cols-3`)
- Проверка дедлайна в Jinja2: `{% if project.deadline and project.deadline < now %}`
- `now` передавать из роутера: `"now": datetime.utcnow()`
- Заметки: белые карточки с инициалами автора (круглый аватар-заглушка)

---

### Проверка

- [ ] `GET /` — список проектов (пустой — OK, без ошибок рендера)
- [ ] `GET /projects/999` → 404
- [ ] coordinator — видит проект, форму добавления не видит
- [ ] member в проекте — видит форму добавления
- [ ] member не в проекте — форму не видит
- [ ] Нет эмодзи в шаблонах

---

### Git

```bash
git add routers/dashboard.py routers/projects.py templates/dashboard.html templates/project_detail.html
git commit -m "feat(pages): dashboard and project detail with role-based write access"
```

---

### Ожидаю:

Dashboard открывается. Страница проекта открывается. Форма добавления заметки управляется ролью.

Когда закончишь — напиши **"проверь"** и жди.
