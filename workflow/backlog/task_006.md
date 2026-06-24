## Task #006 — Заметки: CRUD + файловые вложения (upload/download)

**Тип:** feat
**Приоритет:** High
**Зависит от:** Task #005

---

### Контекст

Ключевая функциональность — создание заметок и прикрепление файлов.
Файлы хранятся в PostgreSQL как bytea. Лимит 10MB на файл.
Удалять заметку может только её автор или admin.

---

### Acceptance Criteria

- [ ] `POST /projects/{project_id}/notes` — создаёт заметку, редирект на `/projects/{id}`
- [ ] `DELETE /notes/{note_id}` — удаляет заметку (только автор или admin), каскадно удаляет вложения
- [ ] `POST /notes/{note_id}/attachments` — загружает файл к заметке
  - Проверка размера: если `> MAX_UPLOAD_BYTES` → HTTP 413 с сообщением
  - Сохраняет: `original_filename`, `file_size`, `content_type`, `file_data` (bytes)
  - `filename` = UUID4
- [ ] `GET /attachments/{attachment_id}/download` — скачивает файл
  - Требует авторизации (любая роль)
  - Заголовки: `Content-Disposition: attachment; filename="original_filename"`, `Content-Type`
- [ ] `DELETE /attachments/{attachment_id}` — удаляет вложение (автор заметки или admin)
- [ ] После всех POST/DELETE → редирект на страницу проекта
- [ ] Форма загрузки файла видна только при наличии права записи

---

### Затрагиваемые файлы

| Действие | Путь |
|---|---|
| создать | `routers/notes.py` |
| изменить | `templates/project_detail.html` (формы upload, кнопки удаления) |

---

### Технические детали

```python
from uuid import uuid4
from fastapi import UploadFile, File, Form, Response
from fastapi.responses import RedirectResponse

@router.post("/projects/{project_id}/notes")
async def create_note(project_id: int, content: str = Form(...),
                      current_user=Depends(get_current_user),
                      db=Depends(get_db_session)):
    if not can_write_to_project(project_id, current_user, db):
        raise HTTPException(403)
    note = Note(project_id=project_id, author_id=current_user.id, content=content)
    db.add(note); db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)

@router.post("/notes/{note_id}/attachments")
async def upload_attachment(note_id: int, file: UploadFile = File(...),
                             current_user=Depends(get_current_user),
                             db=Depends(get_db_session)):
    note = db.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(404)
    if not can_write_to_project(note.project_id, current_user, db):
        raise HTTPException(403)
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Файл превышает лимит {settings.MAX_UPLOAD_BYTES // 1048576}MB")
    attachment = NoteAttachment(
        note_id=note_id, filename=str(uuid4()),
        original_filename=file.filename,
        file_size=len(file_bytes), content_type=file.content_type,
        file_data=file_bytes
    )
    db.add(attachment); db.commit()
    return RedirectResponse(f"/projects/{note.project_id}", status_code=303)

@router.get("/attachments/{attachment_id}/download")
async def download_attachment(attachment_id: int,
                               current_user=Depends(get_current_user),
                               db=Depends(get_db_session)):
    att = db.query(NoteAttachment).filter_by(id=attachment_id).first()
    if not att:
        raise HTTPException(404)
    return Response(
        content=att.file_data,
        media_type=att.content_type,
        headers={"Content-Disposition": f'attachment; filename="{att.original_filename}"'}
    )
```

**Форма загрузки в шаблоне:**
```html
<form action="/notes/{{ note.id }}/attachments" method="post" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <button type="submit">
    <!-- SVG иконка скрепки -->
    Прикрепить файл
  </button>
</form>
```

**Кнопки удаления** реализовать через `<form method="post" action="/notes/{id}/delete">` с hidden input `_method=DELETE` или отдельным POST-роутом `/notes/{id}/delete`.
Использовать POST, не DELETE — для совместимости с HTML формами браузера.

---

### Проверка

- [ ] Создать заметку — появляется в ленте
- [ ] Загрузить файл — появляется ссылка на скачивание (SVG иконка скачивания рядом)
- [ ] Загрузить файл > 10MB → HTTP 413, сервер не падает
- [ ] Скачать файл → браузер скачивает с правильным именем
- [ ] coordinator пытается создать заметку → HTTP 403
- [ ] member не в проекте пытается создать заметку → HTTP 403
- [ ] Нет эмодзи в шаблоне

---

### Git

```bash
git add routers/notes.py templates/project_detail.html
git commit -m "feat(notes): create notes, file upload/download, permission checks"
```

---

### Ожидаю:

Полный цикл: создать заметку → прикрепить файл → скачать → удалить.

Когда закончишь — напиши **"проверь"** и жди.
