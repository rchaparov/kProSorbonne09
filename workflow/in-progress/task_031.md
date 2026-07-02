## Task #031 — Редизайн карточек проектов (Вариант А + мобильная навигация)

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #030

---

### Контекст

Редизайн карточек проектов на дашборде и добавление нижней навигации для мобильных.
Дизайн утверждён — Вариант А из мокапа.

---

### Acceptance Criteria

**Карточки проектов (dashboard.html):**
- [ ] Цветная полоска сверху карточки (3px) по статусу: planning=серый, active=синий, review=amber, on_hold=оранжевый, completed=зелёный
- [ ] Синяя точка-индикатор в правом верхнем углу карточки — показывается если `last_note_at > current_user.last_visit_at` (нужен роутер)
- [ ] Бейдж статуса слева внизу (в footer карточки), дедлайн-бейдж справа вверху
- [ ] Описание проекта — обрезается до 2 строк (`-webkit-line-clamp: 2`)
- [ ] Прогресс-бар сохраняется — цвет меняется на красный при просрочке, зелёный при completed
- [ ] Аватары участников в footer: круглые инициалы (2 буквы), первые 3 + "+N" если больше
- [ ] Время последней активности в footer: "5 мин назад", "2 ч. назад", "вчера", "3 дня назад"
- [ ] Завершённые и приостановленные карточки — `opacity: 0.65`
- [ ] Hover на карточке — лёгкое выделение `border-color` (не shadow)

**Бэкенд (dashboard.py):**
- [ ] Для каждого проекта — `last_note_at`: дата последней заметки (один GROUP BY запрос, не N+1)
- [ ] Передать `last_note_at` per project в контекст шаблона
- [ ] Аватары: для каждого проекта — первые 3 участника с `full_name` (joinedload или отдельный запрос не в цикле)

**Мобильная навигация (base.html):**
- [ ] Нижняя панель `<nav class="bottom-nav">` видна только на мобильных (< md): `md:hidden`
- [ ] 5 пунктов: Проекты (`/`), Материалы (`/materials`), Аналитика (`/analytics`), Уведомления (`/notifications`), Профиль (`/profile`)
- [ ] Активный пункт определяется по `request.url.path` — подсвечивается indigo
- [ ] Счётчик уведомлений (красная точка) на пункте "Уведомления" если `unread_count > 0`
- [ ] `main` контейнер получает `pb-20 md:pb-0` — отступ снизу чтобы контент не перекрывался нижней панелью
- [ ] Верхний navbar на мобильном: скрыть ссылки "Материалы", "Аналитика", "Проекты" (они теперь внизу) — оставить только логотип + иконки поиска/уведомлений/профиля

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| изменить | `routers/dashboard.py` (last_note_at, аватары участников) |
| изменить | `templates/dashboard.html` (редизайн карточек) |
| изменить | `templates/base.html` (нижняя навигация, адаптация верхнего navbar) |
| изменить | `static/css/style.css` (стили карточек, bottom-nav) |

---

### Технические детали

```python
# routers/dashboard.py — last_note_at одним запросом
from sqlalchemy import func

last_note_subq = (
    db.query(Note.project_id, func.max(Note.created_at).label("last_note_at"))
    .group_by(Note.project_id)
    .subquery()
)
last_notes = dict(
    db.query(last_note_subq.c.project_id, last_note_subq.c.last_note_at).all()
)

# Аватары — первые 3 участника на проект, один запрос
from sqlalchemy.orm import joinedload

members_per_project = {}
all_members = (
    db.query(ProjectMember)
    .options(joinedload(ProjectMember.user))
    .filter(ProjectMember.project_id.in_([p.id for p in projects]))
    .all()
)
for m in all_members:
    members_per_project.setdefault(m.project_id, []).append(m.user)

# В контекст:
# "last_notes": last_notes  — dict {project_id: datetime}
# "members_per_project": members_per_project  — dict {project_id: [User]}
```

**Аватар участника — инициалы:**
```python
# В шаблоне Jinja2:
# parts = member.full_name.split()
# initials = (parts[0][0] + parts[1][0]).upper() if len(parts) >= 2 else parts[0][:2].upper()
```

**Время последней активности — JS через data-utc (уже есть `timeAgo()`):**
```html
{% if last_notes.get(project.id) %}
<span class="activity-time">
    <i class="ti ti-message" aria-hidden="true"></i>
    <time data-utc="{{ last_notes[project.id].isoformat() }}" data-timeago>
        {{ last_notes[project.id].strftime('%d.%m') }}
    </time>
</span>
{% endif %}
```

**Цветная полоска и синяя точка:**
```html
{% set status_stripe = {
    'planning': '#888780',
    'active': '#378ADD',
    'review': '#BA7517',
    'on_hold': '#D85A30',
    'completed': '#639922'
} %}

<div class="project-card {% if project.status in ('completed', 'on_hold') %}opacity-65{% endif %}"
     data-project-card data-title="{{ project.title|lower|e }}">
    <div class="card-stripe" style="background: {{ status_stripe.get(project.status, '#888780') }}"></div>
    {% set last_note = last_notes.get(project.id) %}
    {% if last_note and last_note > now - timedelta(hours=24) %}
    <div class="new-event-dot"></div>
    {% endif %}
    ...
```

**Прогресс-бар — цвет по состоянию:**
```python
# В роутере считать progress_color per project:
def progress_color(status: str, deadline, now, pct: int) -> str:
    if status == "completed": return "#639922"
    if deadline and deadline < now: return "#A32D2D"  # просрочен
    return "#378ADD"  # обычный
```

**CSS для карточек (static/css/style.css):**
```css
.project-card {
    background: white;
    border: 0.5px solid var(--border, #e5e7eb);
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: border-color 0.15s;
    position: relative;
}
.project-card:hover { border-color: #6366f1; }

.card-stripe { height: 3px; }

.new-event-dot {
    position: absolute;
    top: 12px; right: 12px;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #378ADD;
    border: 1.5px solid white;
}

.card-avatar {
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 500;
    background: #dbeafe; color: #1e40af;
    border: 1.5px solid white;
    margin-left: -6px;
}
.card-avatar:first-child { margin-left: 0; }
.card-avatar-more { background: #f3f4f6; color: #9ca3af; }

.bottom-nav {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: white;
    border-top: 0.5px solid #e5e7eb;
    display: flex;
    justify-content: space-around;
    padding: 8px 0 max(12px, env(safe-area-inset-bottom));
    z-index: 40;
}
.bottom-nav-item {
    display: flex; flex-direction: column;
    align-items: center; gap: 3px;
    text-decoration: none;
    color: #9ca3af;
    font-size: 9px; font-weight: 500;
    position: relative;
    min-width: 48px;
}
.bottom-nav-item.active { color: #4f46e5; }
.bottom-nav-item i { font-size: 20px; }
.bottom-nav-badge {
    position: absolute; top: -2px; right: 8px;
    width: 7px; height: 7px;
    background: #e24b4a; border-radius: 50%;
    border: 1.5px solid white;
}
```

**base.html — верхний navbar на мобильном:**
Ссылки "Материалы", "Аналитика" в `#nav-links` — добавить класс `hidden md:flex` на их `<div>` контейнер (они уже в `#nav-links` который hidden на мобильном). Пункт "Проекты" dropdown — оставить виден только на md+:
```html
<div class="hidden md:block" id="projects-dropdown-wrapper">...</div>
```

**base.html — нижняя навигация:**
```html
{% if current_user %}
<nav class="bottom-nav md:hidden" aria-label="Мобильная навигация">
    <a href="/" class="bottom-nav-item {% if request.url.path == '/' %}active{% endif %}">
        <i class="ti ti-layout-grid" aria-hidden="true"></i>
        <span>Проекты</span>
    </a>
    <a href="/materials" class="bottom-nav-item {% if request.url.path.startswith('/materials') %}active{% endif %}">
        <i class="ti ti-book" aria-hidden="true"></i>
        <span>Материалы</span>
    </a>
    <a href="/analytics" class="bottom-nav-item {% if request.url.path == '/analytics' %}active{% endif %}">
        <i class="ti ti-chart-bar" aria-hidden="true"></i>
        <span>Аналитика</span>
    </a>
    <a href="/notifications" class="bottom-nav-item {% if request.url.path == '/notifications' %}active{% endif %}" style="position:relative">
        <i class="ti ti-bell" aria-hidden="true"></i>
        {% if unread_count is defined and unread_count > 0 %}
        <span class="bottom-nav-badge"></span>
        {% endif %}
        <span>События</span>
    </a>
    <a href="/profile" class="bottom-nav-item {% if request.url.path == '/profile' %}active{% endif %}">
        <i class="ti ti-user" aria-hidden="true"></i>
        <span>Профиль</span>
    </a>
</nav>
{% endif %}
```

**Tabler icons** — подключить CDN в base.html `<head>`:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.0.0/tabler-icons.min.css">
```
Использовать `<i class="ti ti-NAME">` вместо inline SVG для нижней навигации и аватаров.
Существующие SVG иконки в шаблонах не трогать.

---

### Проверка

- [ ] Карточки показывают цветную полоску по статусу
- [ ] Аватары: первые 3 участника + "+N" если больше 3
- [ ] Время последней активности отображается через timeAgo()
- [ ] Синяя точка на карточках с активностью за последние 24 часа
- [ ] Completed и on_hold карточки приглушены opacity
- [ ] Hover на карточке — indigo border
- [ ] На мобильном (< 768px) нижняя панель видна, верхние ссылки скрыты
- [ ] Активный пункт нижней панели подсвечен indigo
- [ ] Счётчик уведомлений (красная точка) на пункте "События"
- [ ] Контент не перекрывается нижней панелью (pb-20 на main)
- [ ] Нет эмодзи
- [ ] `grep -r "print(" routers/ utils/` — пустой

---

### Git

```bash
git add routers/dashboard.py templates/dashboard.html templates/base.html static/css/style.css
git commit -m "feat(ui): project card redesign variant A, mobile bottom navigation"
```

---

### Ожидаю:

Карточки с цветной полоской, аватарами, временем активности. Мобильная нижняя навигация.

Когда закончишь — напиши **"проверь"** и жди.
