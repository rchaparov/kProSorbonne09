# Task #029 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Double-submit защита: глобальный JS в `base.html` — disable + spinner «Отправка...», fallback 10 сек; исключение `data-no-loading` (поиск)
- Empty states: заметки и чеклист на странице проекта, уведомления, поиск без результатов
- iOS Safari: `openOfficeViewer` открывает через скрытую `<a>` вместо `window.open`; кнопки передают `this`
- iOS Safari: `-webkit-backdrop-filter` на sticky-навигации проекта
- Горячие клавиши: `Ctrl/Cmd+Enter` отправляет форму заметки, `Escape` закрывает reply-плашку; подсказка под textarea
- Flash messages: текущий PRG-подход (`redirect after POST` + `?msg=`) задокументирован как корректный для MVP

## Изменённые файлы
- `templates/base.html` — double-submit JS, openOfficeViewer fix, `data-no-loading` на поиске в nav
- `templates/project_detail.html` — empty states, backdrop-blur webkit, Ctrl+Enter/Escape, openOfficeViewer(this)
- `templates/notifications.html` — empty state «Нет новых уведомлений»
- `templates/search.html` — empty state, `data-no-loading` на форме
- `templates/materials.html` — openOfficeViewer(this)

## Обязательные проверки
- [x] `grep -r "print(" routers/ utils/` — пустой вывод: Да (N/A — только templates)
- [x] Double-submit на POST-формах: Да (глобальный listener)
- [x] `data-no-loading` на GET-поиске: Да
- [x] Empty states: Да
- [x] openOfficeViewer через `<a>` + `this`: Да
- [x] Ctrl+Enter / Escape в форме заметки: Да

## Git
- commit hash: 71ab7f0
- branch: main
- push: ожидает "ПРИНЯТО"

## Замечания / Known issues
- `print()` в `main.py` startup() — вне scope task_029 (заменить на logging отдельно)
- Формы с `data-confirm` не показывают spinner (по спецификации task card)
