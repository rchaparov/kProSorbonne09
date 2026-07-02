# Task #031 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Редизайн карточек проектов (Вариант А): цветная полоска, deadline badge, status в footer, аватары, activity time
- Бэкенд: `last_notes` одним GROUP BY, `members_per_project` одним запросом с joinedload
- Прогресс-бар: цвет по статусу/дедлайну (красный просрочен, зелёный completed)
- Синяя точка при активности заметок за последние 24 часа
- Мобильная нижняя навигация (5 пунктов, Tabler icons CDN)
- Верхний navbar на мобильном: скрыты Projects dropdown, Materials/Analytics links, notifications desktop link
- `main` с `pb-20 md:pb-0`, расширен `timeAgo()` (вчера, N дней назад)

## Изменённые файлы
- `routers/dashboard.py` — last_note_at, members, progress_colors
- `templates/dashboard.html` — новые карточки project-card
- `templates/base.html` — bottom-nav, Tabler CDN, mobile navbar
- `static/css/style.css` — project-card, bottom-nav, card-* стили

## Обязательные проверки
- [x] Цветная полоска по статусу: Да
- [x] Аватары 3 + N: Да
- [x] timeAgo для активности: Да
- [x] Синяя точка (24ч): Да
- [x] opacity completed/on_hold: Да
- [x] Hover border indigo: Да
- [x] Bottom nav mobile: Да
- [x] `grep -r "print(" routers/ utils/` — пустой: Да

## Git
- commit hash: d2a76ea
- branch: main
- push: ожидает "ПРИНЯТО"

## Замечания / Known issues
- `last_visit_at` на User отсутствует — индикатор новых событий по критерию «активность за 24ч» (как в technical details task card)
- Burger menu скрыт — навигация на мобильном только через bottom-nav
