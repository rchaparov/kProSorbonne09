# Task #030 — DONE
**Дата:** 2026-06-24
**Исполнитель:** Cursor Agent

## Что сделано
- Markdown в ленте заметок: `marked.js` + `DOMPurify.sanitize()` через CDN в `base.html`
- Блоки `.note-content` рендерятся при загрузке страницы (заметки и ответы)
- Стили prose-like для markdown в `static/css/style.css`
- Кнопка «Предпросмотр» / «Редактировать» в форме создания заметки
- Подсказка по синтаксису markdown под textarea
- Drag & drop файлов: drop zone с пунктирной границей + drop на textarea
- Та же логика drop zone в форме «+ Добавить файл» на странице материалов
- Глобальные хелперы: `renderMarkdownHtml`, `setupDropZone`, `initMultiFileInputs`

## Изменённые файлы
- `templates/base.html` — CDN marked + DOMPurify, markdown render, drop zone helpers
- `templates/project_detail.html` — `.note-content`, preview, drag & drop, markdown hint
- `templates/materials.html` — drop zone в форме добавления файлов
- `static/css/style.css` — `.note-content` и `.drop-zone` стили

## Обязательные проверки
- [x] Markdown рендерится в ленте (не в textarea): Да
- [x] DOMPurify перед innerHTML: Да
- [x] Preview toggle: Да
- [x] Drop zone visible + drag-over highlight: Да
- [x] Drop на textarea: Да
- [x] `grep -r "print(" routers/ utils/` — пустой вывод: Да (N/A — только frontend)

## Git
- commit hash: 5d43df0
- branch: main
- push: ожидает "ПРИНЯТО"

## Замечания / Known issues
- Live feed (polling) при reload страницы подхватывает markdown render
- `print()` в `main.py` startup() — вне scope (отдельная задача)
