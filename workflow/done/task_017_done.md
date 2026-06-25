# Task #017 — DONE
**Дата:** 2026-06-25
**Исполнитель:** Cursor Agent

## Что сделано
- Миграция `006_note_replies.py`: поля `parent_id`, `quoted_content` в таблице `notes`
- Shallow threading: ответы на один уровень, ответ на ответ прикрепляется к корневой заметке
- Кнопки «Ответить» и «Цитировать» с JS (replyTo, cancelReply, quoteNote)
- Плашка «Ответ на: …» с отменой в форме создания заметки
- Отображение цитаты над текстом заметки и в ответах
- Пагинация корневых заметок: 20 на страницу, replies загружаются вместе с родителем

## Изменённые файлы
- `database.py` — поля `parent_id`, `quoted_content` в модели Note
- `migrations/versions/006_note_replies.py` — новая миграция
- `routers/notes.py` — `parent_id`, `quoted_content` в create_note
- `routers/projects.py` — пагинация и группировка replies
- `templates/project_detail.html` — UI ответов, цитат, пагинация, JS

## Git
- commit hash: [вставить]
- branch: main
- push: ожидает "ПРИНЯТО"

## Тесты
- [ ] Manual check: миграция 006 применяется
- [ ] Manual check: «Ответить» → плашка, parent_id в форме
- [ ] Manual check: «Цитировать» → текст в textarea, quoted_content
- [ ] Manual check: ответ с отступом под родителем
- [ ] Manual check: пагинация при > 20 заметок
- [x] Manual check: import main.py — OK

## Замечания / Known issues
нет
