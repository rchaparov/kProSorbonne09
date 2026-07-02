## Task #030 — Фичи: Markdown в заметках, drag & drop файлы

**Тип:** feat
**Приоритет:** Medium
**Зависит от:** Task #029

---

### Контекст

Две высокоприоритетные пользовательские фичи:
1. Markdown в тексте заметок — через marked.js в браузере, бэкенд не меняется
2. Drag & drop загрузка файлов — нативный dragover/drop на textarea форм

---

### Acceptance Criteria

**1. Markdown рендеринг в заметках**
- [ ] Подключить `marked.js` через CDN: `https://cdn.jsdelivr.net/npm/marked/marked.min.js`
- [ ] При загрузке страницы — заменить `textContent` каждого блока `.note-content` на `innerHTML` с `marked.parse(text)`
- [ ] XSS защита: перед рендером санировать HTML через `marked` с опцией `sanitize` или через простую замену тегов. Использовать `DOMPurify.sanitize()` (тоже CDN: `https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js`)
- [ ] Markdown не рендерится в textarea при редактировании — только в ленте (read-only view)
- [ ] Стили для rendered markdown в `.note-content`: `prose`-like CSS (заголовки, код, цитаты)
- [ ] Подсказка под textarea: `**жирный**, *курсив*, \`код\`, > цитата`
- [ ] Режим preview в форме: кнопка "Предпросмотр" переключает textarea ↔ rendered view

Markdown стили (добавить в `static/css/style.css`):
```css
.note-content h1, .note-content h2, .note-content h3 {
    font-weight: 600; margin-top: 0.75em; margin-bottom: 0.25em;
}
.note-content h1 { font-size: 1.2rem; }
.note-content h2 { font-size: 1.1rem; }
.note-content code {
    background: #f3f4f6; padding: 1px 4px; border-radius: 3px;
    font-family: monospace; font-size: 0.875em;
}
.note-content pre { background: #1e293b; color: #e2e8f0; padding: 12px;
    border-radius: 6px; overflow-x: auto; }
.note-content pre code { background: none; padding: 0; color: inherit; }
.note-content blockquote { border-left: 3px solid #6366f1; padding-left: 12px;
    color: #6b7280; margin: 8px 0; }
.note-content ul, .note-content ol { padding-left: 1.5em; margin: 4px 0; }
.note-content a { color: #4f46e5; text-decoration: underline; }
```

**2. Drag & drop загрузка файлов**
- [ ] Форма создания заметки — drop zone поверх `<input type="file" name="files">`
- [ ] При dragover — визуальное выделение (indigo border + bg-indigo-50)
- [ ] При drop — файлы попадают в FileList input (через DataTransfer)
- [ ] Список выбранных файлов обновляется (уже есть JS для `.multi-file-input`)
- [ ] Drag & drop работает НА САМУ TEXTAREA (перетащить файл прямо на область написания)
- [ ] Drop zone виден всегда (не только при dragover) — пунктирная граница с текстом "Перетащите файлы сюда"
- [ ] Та же логика применяется к форме "+ Добавить файл" в материалах

```javascript
function setupDropZone(dropEl, fileInput) {
    dropEl.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropEl.classList.add('drag-over');
    });
    dropEl.addEventListener('dragleave', function() {
        dropEl.classList.remove('drag-over');
    });
    dropEl.addEventListener('drop', function(e) {
        e.preventDefault();
        dropEl.classList.remove('drag-over');
        const dt = new DataTransfer();
        // Добавить уже выбранные файлы
        Array.from(fileInput.files || []).forEach(f => dt.items.add(f));
        // Добавить перетащенные файлы
        Array.from(e.dataTransfer.files).forEach(f => dt.items.add(f));
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change'));
    });
}
```

Drop zone CSS (в `static/css/style.css`):
```css
.drop-zone {
    border: 2px dashed #d1d5db;
    border-radius: 8px;
    padding: 12px;
    transition: all 0.15s;
    cursor: pointer;
}
.drop-zone.drag-over {
    border-color: #6366f1;
    background-color: #eef2ff;
}
```

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| изменить | `templates/base.html` (CDN: marked.js + DOMPurify) |
| изменить | `templates/project_detail.html` (markdown render, preview button, drag & drop) |
| изменить | `templates/materials.html` (drag & drop в форме материала) |
| изменить | `static/css/style.css` (note-content prose стили + drop-zone стили) |

---

### Проверка

- [ ] Создать заметку с `**жирный текст**` → в ленте отображается жирным (не с звёздочками)
- [ ] Создать заметку с `\`код\`` → отображается моноширинным в серой подложке
- [ ] Кнопка "Предпросмотр" показывает rendered markdown до отправки
- [ ] XSS: создать заметку с `<script>alert(1)</script>` → не выполняется (DOMPurify)
- [ ] Перетащить файл на textarea → файл появляется в списке выбранных
- [ ] Перетащить 2 файла → оба в списке
- [ ] Drag over → indigo граница видна
- [ ] Drop zone виден без наведения (пунктирная граница)

---

### Git

```bash
git add templates/ static/
git commit -m "feat(notes): markdown rendering with DOMPurify, drag-and-drop file upload"
```

---

### Ожидаю:

Заметки рендерят Markdown. Файлы можно перетаскивать. XSS защита работает.

Когда закончишь — напиши **"проверь"** и жди.
