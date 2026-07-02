## Task #032 — Расширенная аналитика: команда и проект

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #031

---

### Контекст

Два направления:
1. Обновить `/analytics` — добавить спарклайн активности, динамику vs прошлая неделя, топ участников по заметкам
2. Добавить блок аналитики на странице проекта — метрики, спарклайн, участие, состояние чеклиста, файловая статистика

Без новых таблиц в БД и внешних chart-библиотек — только SQL-запросы и CSS div-бары/спарклайны.

---

### Acceptance Criteria

**1. `/analytics` — новые блоки:**

- [ ] Три метрики вверху (сейчас нет): "Активных проектов N из K всего", "Заметок за 7 дней N", "Средний прогресс N%"
- [ ] Динамика заметок: сравнение текущей и прошлой недели — бейдж "↑ +N vs прошлая неделя" или "↓ -N"
- [ ] Спарклайн активности за 14 дней — 14 div-баров пропорциональной высоты, подписи дат по краям
- [ ] Топ-5 участников по заметкам за всё время — список с аватаром (инициалы), именем, счётчиком
- [ ] Нагрузка по участникам — горизонтальные бары (уже есть, оставить)
- [ ] Сравнение проектов по прогрессу — горизонтальные бары с % для каждого активного проекта, цвет по статусу
- [ ] Блок риска (уже есть, оставить)

**2. `/projects/{id}` — новый блок "Аналитика проекта":**

- [ ] Блок располагается в правой колонке ПОД лентой заметок (не между чеклистом и заметками)
- [ ] Три метрики: прогресс (%), всего заметок, дней до дедлайна (или "просрочен на N дн.")
- [ ] Спарклайн активности заметок за 14 дней
- [ ] Участие в проекте: топ-5 участников по количеству заметок в этом проекте — горизонтальные бары
- [ ] Состояние чеклиста: выполнено X/Y, просрочено N (дедлайн < now и is_done=False), без ответственного M (нет assignees)
- [ ] Файловая статистика: кол-во вложений в заметках, кол-во прикреплённых материалов из базы знаний

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| изменить | `routers/analytics.py` (новые запросы) |
| изменить | `routers/projects.py` (запросы для аналитики проекта) |
| изменить | `templates/analytics.html` (новые блоки) |
| изменить | `templates/project_detail.html` (блок аналитики проекта) |

---

### Технические детали

```python
# routers/analytics.py — новые запросы

from datetime import datetime, timedelta
now = datetime.utcnow()
week_ago = now - timedelta(days=7)
two_weeks_ago = now - timedelta(days=14)

# Динамика заметок
notes_this_week = db.query(func.count(Note.id)).filter(Note.created_at >= week_ago).scalar() or 0
notes_prev_week = db.query(func.count(Note.id)).filter(
    Note.created_at >= two_weeks_ago,
    Note.created_at < week_ago
).scalar() or 0
notes_delta = notes_this_week - notes_prev_week

# Спарклайн: кол-во заметок по дням за 14 дней
sparkline_data = []
for i in range(13, -1, -1):  # от -13 до 0 дней назад
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
    day_end = day_start + timedelta(days=1)
    count = db.query(func.count(Note.id)).filter(
        Note.created_at >= day_start,
        Note.created_at < day_end
    ).scalar() or 0
    sparkline_data.append({"date": day_start, "count": count})
sparkline_max = max((d["count"] for d in sparkline_data), default=1) or 1

# Топ-5 участников по заметкам
top_authors = (
    db.query(User, func.count(Note.id).label("note_count"))
    .join(Note, Note.author_id == User.id)
    .group_by(User.id)
    .order_by(func.count(Note.id).desc())
    .limit(5)
    .all()
)

# Сравнение проектов по прогрессу (активные)
active_projects = db.query(Project).filter(
    Project.status.notin_(["completed"])
).order_by(Project.title).all()
project_progress_list = []
for p in active_projects:
    total = db.query(func.count(ChecklistItem.id)).filter_by(project_id=p.id).scalar() or 0
    done = db.query(func.count(ChecklistItem.id)).filter_by(project_id=p.id, is_done=True).scalar() or 0
    pct = project_progress(p.status, done, total)
    project_progress_list.append({"project": p, "pct": pct, "done": done, "total": total})
project_progress_list.sort(key=lambda x: x["pct"], reverse=True)

# Передать в контекст:
# "notes_this_week": notes_this_week
# "notes_delta": notes_delta
# "sparkline_data": sparkline_data
# "sparkline_max": sparkline_max
# "top_authors": top_authors
# "project_progress_list": project_progress_list
# "total_projects": total_projects
# "active_projects_count": sum(1 for p in db.query(Project).all() if p.status not in ("completed",))
```

```python
# routers/projects.py — добавить в контекст project_detail

# Спарклайн активности заметок за 14 дней
project_sparkline = []
for i in range(13, -1, -1):
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
    day_end = day_start + timedelta(days=1)
    count = db.query(func.count(Note.id)).filter(
        Note.project_id == project_id,
        Note.created_at >= day_start,
        Note.created_at < day_end
    ).scalar() or 0
    project_sparkline.append(count)
project_sparkline_max = max(project_sparkline, default=1) or 1

# Топ участников по заметкам в этом проекте
project_top_authors = (
    db.query(User, func.count(Note.id).label("note_count"))
    .join(Note, Note.author_id == User.id)
    .filter(Note.project_id == project_id, Note.parent_id.is_(None))
    .group_by(User.id)
    .order_by(func.count(Note.id).desc())
    .limit(5)
    .all()
)
project_top_max = project_top_authors[0][1] if project_top_authors else 1

# Состояние чеклиста
checklist_overdue = db.query(func.count(ChecklistItem.id)).filter(
    ChecklistItem.project_id == project_id,
    ChecklistItem.is_done.is_(False),
    ChecklistItem.deadline < now,
    ChecklistItem.deadline.isnot(None)
).scalar() or 0

# Без ответственного (нет assignees)
all_item_ids = [i.id for i in checklist_items]
assigned_item_ids = set(
    row[0] for row in
    db.query(ChecklistItemAssignee.item_id)
    .filter(ChecklistItemAssignee.item_id.in_(all_item_ids))
    .all()
) if all_item_ids else set()
checklist_unassigned = sum(1 for i in checklist_items if not i.is_done and i.id not in assigned_item_ids)

# Файловая статистика
note_ids = [n["note"].id for n in note_items] if note_items else []
attachments_count = db.query(func.count(NoteAttachment.id)).filter(
    NoteAttachment.note_id.in_(note_ids)
).scalar() or 0 if note_ids else 0

materials_count = db.query(func.count(NoteMaterialLink.id)).filter(
    NoteMaterialLink.note_id.in_(note_ids)
).scalar() or 0 if note_ids else 0

total_notes_count = db.query(func.count(Note.id)).filter_by(project_id=project_id).scalar() or 0

# Передать в контекст:
# "project_sparkline": project_sparkline
# "project_sparkline_max": project_sparkline_max
# "project_top_authors": project_top_authors
# "project_top_max": project_top_max
# "checklist_overdue": checklist_overdue
# "checklist_unassigned": checklist_unassigned
# "attachments_count": attachments_count
# "materials_count": materials_count
# "total_notes_count": total_notes_count
```

**Спарклайн (CSS div-бары, без библиотек):**
```html
<!-- В analytics.html и project_detail.html -->
<div style="display:flex;align-items:flex-end;gap:3px;height:40px;">
    {% for day in sparkline_data %}
    {% set h = (day.count / sparkline_max * 100)|round|int %}
    <div style="flex:1;border-radius:2px 2px 0 0;background:#378ADD;opacity:0.7;
                height:{{ [h, 5]|max }}%;min-height:2px;"
         title="{{ day.date.strftime('%d.%m') }}: {{ day.count }} заметок"></div>
    {% endfor %}
</div>
<div style="display:flex;justify-content:space-between;margin-top:4px">
    <span style="font-size:10px;color:#9ca3af">{{ sparkline_data[0].date.strftime('%d.%m') }}</span>
    <span style="font-size:10px;color:#9ca3af">{{ sparkline_data[-1].date.strftime('%d.%m') }}</span>
</div>
```

**Три метрики вверху analytics.html:**
```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px">
    <div class="bg-white shadow rounded-lg p-4">
        <p style="font-size:11px;color:#9ca3af;margin-bottom:4px">Активных проектов</p>
        <p style="font-size:26px;font-weight:500">{{ active_projects_count }}</p>
        <p style="font-size:11px;color:#9ca3af">из {{ total_projects }} всего</p>
    </div>
    <div class="bg-white shadow rounded-lg p-4">
        <p style="font-size:11px;color:#9ca3af;margin-bottom:4px">Заметок за 7 дней</p>
        <p style="font-size:26px;font-weight:500">{{ notes_this_week }}</p>
        <p style="font-size:11px;
            color:{% if notes_delta >= 0 %}#3B6D11{% else %}#A32D2D{% endif %}">
            {% if notes_delta >= 0 %}↑ +{% else %}↓ {% endif %}{{ notes_delta|abs }} vs прошлая неделя
        </p>
    </div>
    <div class="bg-white shadow rounded-lg p-4">
        <p style="font-size:11px;color:#9ca3af;margin-bottom:4px">Средний прогресс</p>
        <p style="font-size:26px;font-weight:500">{{ avg_progress }}%</p>
        <p style="font-size:11px;color:#9ca3af">по активным проектам</p>
    </div>
</div>
```

**Блок аналитики проекта в project_detail.html:**
Добавить в правую колонку (`lg:col-span-2`) после ленты заметок, отдельной карточкой с заголовком "Аналитика":
```html
<div id="section-analytics" class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Аналитика</h2>
    <!-- три метрики, спарклайн, участие, чеклист, файлы -->
</div>
```

Якорная навигация: добавить "Аналитика" четвёртым пунктом в sticky-панель проекта.

---

### Проверка

```bash
python tests/smoke_test.py
```

- [ ] smoke_test.py — все OK
- [ ] `/analytics` открывается, три метрики отображаются
- [ ] Спарклайн 14 баров виден на странице команды и проекта
- [ ] Динамика "↑ +N" или "↓ -N" корректна (0 не показывает ни ↑ ни ↓ — показывает "= 0")
- [ ] Топ-5 авторов отображается с аватарами
- [ ] Сравнение проектов по прогрессу: бары разного цвета по статусу
- [ ] Блок аналитики на странице проекта виден ниже ленты заметок
- [ ] Состояние чеклиста: числа "просрочено" и "без ответственного" корректны
- [ ] Якорная навигация: "Аналитика" четвёртым пунктом

---

### Git

```bash
git add routers/analytics.py routers/projects.py templates/analytics.html templates/project_detail.html
git commit -m "feat(analytics): sparkline, team top-authors, project detail analytics block"
```

---

### Ожидаю:

Полная аналитика команды с динамикой. Блок аналитики внутри каждого проекта.

Когда закончишь — напиши **"проверь"** и жди.
