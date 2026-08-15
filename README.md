# Telegram Publisher — mobile-friendly

Этот вариант вообще не использует OpenAI API.

Схема:

```text
ChatGPT на телефоне
        ↓
копируете готовый Telegram-пост
        ↓
GitHub → telegram-draft.md → Edit
        ↓
Paste → Commit
        ↓
GitHub Actions
        ↓
Telegram Bot API
        ↓
Telegram-канал
```

## Один раз настроить GitHub

### Secret

`Settings → Secrets and variables → Actions → Secrets`

```text
TELEGRAM_BOT_TOKEN
```

Используйте новый Telegram bot token.

### Variable

`Settings → Secrets and variables → Actions → Variables`

```text
TELEGRAM_CHAT_ID=-1003337129017
```

## Как публиковать с телефона

1. Откройте GitHub в браузере на телефоне.
2. Откройте репозиторий.
3. Откройте `telegram-draft.md`.
4. Нажмите кнопку редактирования.
5. Удалите старый текст.
6. Вставьте Telegram-пост из ChatGPT.
7. Нажмите `Commit changes`.
8. GitHub Actions автоматически запустит публикацию.
9. После успешной отправки копия поста сохранится в `published/`.

## Markdown

Можно писать обычный удобный Markdown:

```md
**AI Engineering Digest**

**1. Self-Evolving Coding Agents**

Что произошло...

`Agent → MR → Review → Skill`

[Исследование](https://example.com)
```

Скрипт сам преобразует его в Telegram MarkdownV2 и экранирует специальные символы.

Поддерживаются:

- `**жирный текст**`
- `` `inline code` ``
- `[ссылка](https://...)`

Обычный текст автоматически экранируется под Telegram MarkdownV2.

## Длинные посты

Telegram ограничивает длину одного сообщения.

Скрипт автоматически разбивает длинный пост примерно по 3500 символов и отправляет несколько сообщений подряд.

## Архив

После каждой успешной публикации создаётся файл:

```text
published/
  2026-08-15_14-52-03_a12bc34d.md
```

Так можно видеть историю всех реально опубликованных сообщений.

## Как полностью остановить публикацию

`GitHub → Actions → Publish Telegram Draft → ... → Disable workflow`

Либо удалить trigger по `push` из `.github/workflows/publish.yml`.

## Важно

Любой commit в `main`, который изменяет `telegram-draft.md`, означает:

**опубликовать содержимое файла в Telegram.**

Поэтому не редактируйте этот файл для черновика, если не хотите сразу публиковать.
