# Hotfix admin nav — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Удалены мёртвые burger-btn, inline-CSS `.menu-open` и JS-обработчик из `base.html`
- В mobile bottom-nav добавлен пункт «Админка» (`ti-settings`) только для `system_role == 'admin'`, перед «Профилем»
- Active-подсветка по `request.url.path.startswith('/admin')`
- Десктопная ссылка «Администрирование» в `#nav-links` без изменений

## Изменённые файлы
- `templates/base.html` — удалён бургер, добавлен пункт bottom-nav для admin
- `tests/smoke_test.py` — убран `menu-open` из known_app_classes

## Результаты обязательного чеклиста
- [x] python -m py_compile — без ошибок: Да (N/A, бэкенд не менялся)
- [x] grep print() — пустой: Да
- [x] grep Jinja2Templates — пустой: Да
- [x] grep isinstance RedirectResponse — пустой: Да
- [x] alembic check: N/A
- [x] position:fixed элементы имеют media query скрытия: Да
- [x] новые CSS классы определены в style.css или Tailwind: N/A
- [x] `<a>` как карточка: display:block/width:100% в style.css: Да
- [x] python tests/smoke_test.py — все OK: Да (7/7)

## Git
- commit hash: 0cda3a8
- push: ожидает «ПРИНЯТО»

## Замечания
нет
