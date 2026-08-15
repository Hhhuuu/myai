# Autonomous AI Engineering Digest → Telegram

Полностью автономный pipeline:

```text
GitHub Actions schedule
        ↓
OpenAI Responses API + Web Search
        ↓
AI Engineering Digest
        ├── полный выпуск → digests/YYYY-MM-DD.md
        └── Telegram preview → telegram.md
        └── Telegram payload MarkdownV2 → telegram.json
        ↓
Telegram Bot API
        ↓
Telegram-канал
        ↓
state/latest.json
        ↓
следующий выпуск знает дату и предыдущие темы
```

Своего сервера не требуется.

## Что нужно настроить

### 1. OpenAI API key

Создайте API key в OpenAI API Platform.

В GitHub:

`Settings → Secrets and variables → Actions → Secrets → New repository secret`

Создайте secret:

```text
OPENAI_API_KEY
```

Значение — ваш OpenAI API key.

Важно: подписка ChatGPT и использование OpenAI API тарифицируются отдельно.

### 2. Telegram token

Создайте secret:

```text
TELEGRAM_BOT_TOKEN
```

Бот должен быть администратором Telegram-канала и иметь право Post Messages.

Если прежний bot token уже публиковался в переписке, перевыпустите его через BotFather.

### 3. Telegram chat ID

`Settings → Secrets and variables → Actions → Variables`

Создайте repository variable:

```text
TELEGRAM_CHAT_ID=-1003337129017
```

### 4. Модель OpenAI

Опционально создайте repository variable:

```text
OPENAI_MODEL=gpt-5.6-terra
```

Если переменной нет, используется `gpt-5.6-terra`.

Модель выбирается отдельно от промпта, поэтому её можно менять без изменения кода.

## Первый запуск

Откройте:

`Actions → Generate and publish AI Engineering Digest → Run workflow`

Параметр `publish`:

- `true` — сгенерировать и отправить в Telegram;
- `false` — только сгенерировать и сохранить результат.

Для первой проверки разумно сначала использовать `publish=false`.

После генерации появятся:

```text
digests/YYYY-MM-DD.md   полный выпуск
telegram.md             человекочитаемый preview
telegram.json           готовые сообщения Telegram MarkdownV2
state/latest.json       состояние предыдущих выпусков
```

После проверки запустите ещё раз с `publish=true`.

## Автоматическое расписание

Workflow настроен на:

```text
понедельник, 09:00, Europe/Berlin
```

Файл:

```text
.github/workflows/digest.yml
```

Настройка:

```yaml
schedule:
  - cron: "0 9 * * 1"
    timezone: "Europe/Berlin"
```

## Как исключаются повторы

`state/latest.json` содержит:

- время последнего успешного выпуска;
- период предыдущего выпуска;
- до 100 уже опубликованных заголовков;
- последние источники.

Следующий prompt получает эту информацию и должен включать только события после предыдущего запуска либо существенные новые развития старой темы.

## Где менять правила дайджеста

Весь редакционный prompt находится здесь:

```text
config/digest-prompt.md
```

Можно менять:
- компании;
- приоритеты;
- структуру;
- стиль Telegram-поста;
- требования к источникам;
- количество практических рекомендаций.

## Почему используется Web Search OpenAI

Responses API позволяет подключить встроенный `web_search` tool. Поэтому GitHub Action не содержит собственного crawler/search-engine и не требует отдельных Bing/Google API keys.

## Telegram

Telegram `sendMessage` поддерживает `parse_mode=MarkdownV2`.

Модель сразу генерирует 2–4 самостоятельных сообщения длиной до 3500 символов.
Каждое сообщение должно быть валидным Telegram MarkdownV2 и не содержать
форматирование, разорванное между частями.

`scripts/send_telegram.py` читает `telegram.json` и отправляет сообщения
с `parse_mode=MarkdownV2`.

Это позволяет использовать:
- **жирный текст**;
- *курсив*;
- inline code и code blocks;
- кликабельные ссылки;
- цитаты.

`telegram.md` остаётся preview-файлом для просмотра результата человеком.

## Структура проекта

```text
.
├── .github/
│   └── workflows/
│       └── digest.yml
├── config/
│   └── digest-prompt.md
├── digests/
├── scripts/
│   ├── generate_digest.py
│   └── send_telegram.py
├── state/
│   └── latest.json
├── telegram.md
├── telegram.json
├── requirements.txt
└── README.md
```

## Что происходит при ошибке

Если OpenAI API или Telegram API возвращает ошибку, job завершается ошибкой.

Состояние и новый digest коммитятся только после успешной публикации (либо после генерации при ручном запуске с publish=false — шаг публикации пропущен, а артефакты коммитятся).

Таким образом следующий scheduled run не должен считать неуспешную публикацию завершённым выпуском.

## Стоимость

Основная стоимость — вызов OpenAI API с web search и генерацией полного дайджеста. GitHub Actions для небольшого weekly workflow обычно потребляет лишь несколько минут runner time.

Для уменьшения стоимости можно поменять `OPENAI_MODEL` на более экономичную модель, если она поддерживает web search и даёт приемлемое качество.
