## Task #029 — Фронтенд UX: double-submit, empty states, iOS фиксы, горячие клавиши

**Тип:** feat + fix
**Приоритет:** High
**Зависит от:** Task #028

---

### Контекст

UX аудит выявил раздражающие проблемы: дублирование заметок при медленном интернете,
пустые страницы без подсказок, сломанный Office Viewer на iOS.

---

### Acceptance Criteria

**1. Double-submit защита на формах**
- [ ] В `base.html` глобальный JS: при отправке любой формы — кнопка submit становится disabled и показывает spinner
- [ ] Исключение: формы с `data-no-loading` (поиск, фильтры — они не должны блокироваться)
- [ ] Текст кнопки меняется на "Отправка..." (или spinner SVG) на время ожидания
- [ ] При ошибке (страница перезагрузилась) — кнопка снова активна автоматически (т.к. страница перезагружается)

```javascript
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.dataset.noLoading !== undefined) return;
    if (form.dataset.confirm) return; // confirm уже обработан другим listener
    const submitBtn = form.querySelector('[type="submit"]:not([data-no-loading])');
    if (!submitBtn) return;
    submitBtn.disabled = true;
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<svg class="animate-spin w-4 h-4 inline mr-1" ...></svg> Отправка...';
    // Fallback: разблокировать через 10 сек на случай ошибки сети
    setTimeout(function() {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }, 10000);
});
```

**2. Empty states**
- [ ] Страница проекта без заметок — блок с подсказкой:
  ```html
  {% if not note_items and can_write %}
  <div class="text-center py-12 text-gray-400">
      <svg ...><!-- document-plus icon --></svg>
      <p class="mt-2 text-sm">Нет заметок. Добавьте первую.</p>
  </div>
  {% elif not note_items %}
  <div class="text-center py-12 text-gray-400 text-sm">Заметок пока нет.</div>
  {% endif %}
  ```
- [ ] Страница чеклиста без пунктов — аналогичный empty state
- [ ] Страница уведомлений без уведомлений — "Нет новых уведомлений"
- [ ] `/search` без результатов — "Ничего не найдено по запросу «{{ q }}»"

**3. iOS Safari: Office Viewer через ссылку вместо window.open**

`window.open()` в async функции блокируется iOS Safari popup blocker.

- [ ] В `base.html` функцию `openOfficeViewer` переписать:
  ```javascript
  async function openOfficeViewer(fileType, fileId, btnEl) {
      // Создать скрытую ссылку и кликнуть — iOS Safari не блокирует
      try {
          const originalText = btnEl ? btnEl.innerHTML : '';
          if (btnEl) btnEl.disabled = true;

          const resp = await fetch('/files/temp', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({file_type: fileType, file_id: fileId})
          });
          if (resp.status === 503) {
              alert('Просмотрщик не настроен. Обратитесь к администратору.');
              return;
          }
          if (!resp.ok) throw new Error('Server error');
          const data = await resp.json();

          // Открыть через невидимую ссылку (работает на iOS Safari)
          const a = document.createElement('a');
          a.href = data.viewer_url;
          a.target = '_blank';
          a.rel = 'noopener noreferrer';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
      } catch (e) {
          alert('Не удалось открыть просмотрщик. Попробуйте скачать файл.');
      } finally {
          if (btnEl) {
              btnEl.disabled = false;
          }
      }
  }
  ```
- [ ] В шаблонах заменить `onclick="openOfficeViewer('...', {{ id }})"` на `onclick="openOfficeViewer('...', {{ id }}, this)"`

**4. iOS Safari: backdrop-blur с -webkit- префиксом**
- [ ] В `templates/project_detail.html` sticky-навигация:
  ```html
  style="-webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);"
  ```
  Или добавить в `static/css/style.css`:
  ```css
  .sticky-nav { -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); }
  ```

**5. Горячие клавиши в форме заметки**
- [ ] `Ctrl+Enter` (или `Cmd+Enter` на Mac) в textarea → отправляет форму создания заметки
- [ ] `Escape` → очищает форму, если она раскрыта / закрывает reply-плашку
- [ ] Добавить подсказку под textarea: `<span class="text-xs text-gray-400">Ctrl+Enter для отправки</span>`

```javascript
// В project_detail.html
const noteTextarea = document.querySelector('textarea[name="content"]');
if (noteTextarea) {
    noteTextarea.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const form = this.closest('form');
            if (form) form.requestSubmit();
        }
        if (e.key === 'Escape') {
            cancelReply(); // уже существует
        }
    });
}
```

**6. Cookie-based flash messages (упрощённый вариант)**
- [ ] Оставить текущий `?msg=` подход для MVP (cookie-based flash — отдельная таска)
- [ ] Но добавить `<meta http-equiv="refresh">` защиту — при F5 на странице с `?msg=` браузер не переотправляет форму (это уже работает т.к. мы делаем redirect after POST — PRG pattern). Задокументировать что текущий подход корректен.

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| изменить | `templates/base.html` (double-submit JS, openOfficeViewer fix) |
| изменить | `templates/project_detail.html` (empty states, Ctrl+Enter, backdrop-blur webkit) |
| изменить | `templates/notifications.html` (empty state) |
| изменить | `templates/search.html` (empty state) |
| изменить | `templates/materials.html` (передать this в openOfficeViewer) |

---

### Проверка

- [ ] Медленное соединение (Network throttle): отправить заметку — кнопка становится disabled, spinner виден
- [ ] Страница проекта без заметок — виден empty state с подсказкой
- [ ] Страница уведомлений без уведомлений — "Нет новых уведомлений"
- [ ] iOS Safari: нажать "Просмотр" на DOCX → открывается Office Online (не заблокирован popup)
- [ ] `Ctrl+Enter` в textarea → заметка отправляется
- [ ] `Escape` в textarea → reply-плашка скрывается

---

### Git

```bash
git add templates/ static/
git commit -m "feat(ux): double-submit protection, empty states, iOS Safari fixes, keyboard shortcuts"
```

---

### Ожидаю:

Нет дублирования форм. Empty states на пустых страницах. Office Viewer работает на iOS. Ctrl+Enter отправляет.

Когда закончишь — напиши **"проверь"** и жди.
