**🤖 AI Engineering Digest — главное за неделю**

📅 **Период: 29 сентября – 5 октября 2026**

На этой неделе главный сдвиг снова происходит не в моделях.

Вокруг Coding Agent начинает формироваться вполне обычная инженерная инфраструктура: workflow engine, tool gateway, policies, code review API и отдельный слой подготовки контекста.

Всё больше похоже на то, что production Agentic SDLC будет строиться не как:

Prompt → Agent → Code

а как:

Spec → Context → Workflow → Agent → Policy → Tools → Verification → Review


**1. Workflow-as-Code вместо «пусть агент сам разберётся»**

GitHub представил Dynamic Workflows для Copilot.

Теперь можно программно определить:

— какие стадии проходит задача
— что выполняется параллельно
— где вызывается Agent
— какие structured results он должен вернуть
— где нужен verification
— где процесс должен остановиться и дождаться человека

Например:

Release Checks → Agent analyzes failures → Human Checkpoint → Fix Agent → Verification

Или:

Research → Plan → Implementation → Verification

Это важное разделение:

Orchestrator ≠ Agent

Агенту оставляют анализ и принятие локальных решений.

Сам инженерный процесс становится детерминированным кодом.

Для SDD это особенно интересно: specification может описывать не только результат, но и workflow, через который изменение должно пройти.

⭐ **Практическая ценность:** 5/5
🧪 **Зрелость:** раннее внедрение

[Источник — GitHub Dynamic Workflows](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/)


**2. Uber построил MCP Gateway на 800+ серверов и 5000+ tools**

Очень интересная архитектура от Uber.

Вместо того чтобы каждая команда самостоятельно подключала MCP, компания сделала общую платформу:

Existing API → MCP Registry → Gateway → Auth / Policy / Redaction → Agent

Причём HTTP, gRPC и TChannel API можно автоматически превратить в MCP tools.

Новые tools появляются disabled-by-default и должны быть разрешены владельцем сервиса.

Но ещё интереснее решение проблемы context bloat.

Uber не кладёт определения всех 5000 tools в контекст модели.

Agent постепенно делает:

Discover Server → Discover Tools → Get Schema → Invoke Tool

А для Coding Agents используется Code Mode: большой ответ инструмента можно сохранить в файл, после чего агент прочитает только нужные части.

Это уже важный architectural pattern:

Tool Discovery ≠ Tool Context

Все возможности платформы совершенно не обязательно постоянно держать перед моделью.

⭐ **Практическая ценность:** 5/5
🧪 **Зрелость:** production

[Источник — Uber Engineering: Designing MCP Gateway](https://www.uber.com/us/en/blog/designing-mcp-gateway/)


**3. AI Code Review становится обычным API**

GitHub открыл Copilot Code Review через REST и GraphQL.

Это небольшое с виду изменение сильно влияет на процесс.

Теперь AI Review не обязательно запускать человеком кнопкой в UI.

Можно встроить его непосредственно в SDLC:

PR → Build → Tests → Static Analysis → AI Review → Policy → Human Review → Merge

Например, автоматически запускать глубокий AI Review:

— для изменений public API
— для больших diff
— для security-sensitive компонентов
— перед release
— после изменений, сделанных Coding Agent

При этом важное разделение остаётся:

AI Review ≠ Final Approval

Это дополнительный quality gate, а не замена владельца кода.

⭐ **Практическая ценность:** 5/5
🧪 **Зрелость:** можно применять

[Источник — GitHub Copilot Code Review API](https://github.blog/changelog/2026-10-02-copilot-code-review-api-support-and-new-default-effort-level/)


**4. Большой Spec сам по себе не спасает Coding Agent**

Вышел довольно показательный benchmark LoLBench.

100 задач.

29 крупных software systems.

Средний repository — около 2,4 млн строк кода.

Описание задачи — около 5000 слов.

Reference implementation — около 5500 изменённых строк.

Лучший из 28 протестированных agents полностью решил только 14% задач.

Одна из главных причин — агент плохо определяет, где именно в огромной системе нужно делать изменение.

Но когда ему дополнительно давали правильное дерево релевантных файлов и API specifications, success rate рос на 16–22 процентных пункта.

Для SDD отсюда следует очень важный вывод.

Недостаточно:

Requirement → Specification → Coding Agent

Нужен ещё слой:

Specification → Repository Map → Relevant Components → API Contracts → Coding Agent

То есть:

SDD + Context Engineering

похоже, должны развиваться вместе.

⭐ **Практическая ценность:** 5/5
🧪 **Зрелость:** research, но очень прикладной

[Исследование — LoLBench](https://arxiv.org/abs/2609.37143)


**5. Agent ≠ Policy Engine**

Ещё одно интересное исследование — HiSentinel.

Авторы поставили перед Coding Agent небольшой дополнительный model, который проверяет действие до выполнения.

Для каждого шага он выбирает:

Allow

Redirect

Human Assistance

То есть вместо:

Agent → Action → Error → Recovery

получается:

Agent → Proposed Action → Sentinel → Execute

В экспериментах такой подход повысил completion rate до 14% на одном из benchmark.

Идея особенно интересна для корпоративных платформ.

Например, Sentinel или Policy Layer можно поставить перед:

— git push
— release/tag
— удалением файлов
— database migration
— production tools
— использованием secrets

То есть Coding Agent больше не должен одновременно быть и исполнителем, и тем, кто решает, можно ли ему выполнять собственное действие.

⭐ **Практическая ценность:** 4/5
🧪 **Зрелость:** research / хороший кандидат для пилота

[Исследование — HiSentinel](https://arxiv.org/abs/2609.39957)


**💡 Что можно попробовать**

**1. Agent Workflow-as-Code**

Взять один длинный процесс — например feature implementation или release — и явно описать:

Spec → Plan → Coding Agent → Tests → Review → Human Gate

Не позволять одному Agent самому придумывать весь lifecycle задачи.


**2. MCP Registry**

Перед тем как создавать десятки MCP integrations, завести единый каталог:

Tool → Owner → Permissions → Description → Version → Status

А самим агентам отдавать tools динамически.


**3. AI Review Gate**

После CI автоматически отправлять MR в AI Code Review.

Но использовать его как дополнительный signal перед человеком, а не как автоматическое разрешение merge.


**4. Repository Grounding**

Перед Coding Agent автоматически собирать:

Relevant Files + APIs + Dependencies + ADR + Existing Tests

И только потом отдавать specification.


**5. Pre-execution Policy**

Начать хотя бы с пяти операций:

Deploy

Release

Push

Delete

Secrets

Перед их выполнением Agent должен получить отдельное разрешение policy layer или человека.


**Главный вывод недели**

Agentic Development начинает повторять путь обычных production-систем.

Сначала был один Agent с большим prompt.

Теперь вокруг него постепенно появляются:

Workflow Engine + Context Layer + Tool Gateway + Policy + Observability + Verification + Review

И, похоже, именно качество этой инфраструктуры, а не только выбор модели, будет определять насколько далеко можно безопасно делегировать разработку AI-агентам.