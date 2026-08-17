**🤖 AI Engineering Digest — главное за неделю**

📅 **Период: 10–17 августа 2026**

Главный тренд недели: AI Engineering всё меньше упирается в «какая модель лучше пишет код» и всё больше — в инфраструктуру вокруг агента.

Свежие исследования показывают, что coding agents часто ошибаются ещё **до генерации кода**: неправильно понимают требования или не определяют, какая версия требований сейчас актуальна. А GitHub, OpenAI и Cursor параллельно двигаются к переносимым Skills, persistent memory и воспроизводимым средам исполнения.

**1. Агенту нужен Active Contract, а не просто длинная история Jira**

Вышла интересная работа SpecPath. Авторы давали coding agents разные истории требований, которые в итоге приводили к **одному и тому же финальному контракту**.

Среди 100 запусков, которые успешно решили задачу по прямой спецификации, **35 провалились хотя бы на одной эквивалентной истории изменений**.

`More Context ≠ Better Context`

Jira и Confluence — это история. Агенту нужен текущий state:

`Jira + ADR + comments → Active Contract → Plan → Code`

⭐ **Практическая ценность:** 5/5  
🧪 **Зрелость:** эксперимент → уже можно пилотировать

---

**2. Requirement Engineering становится частью Agent Pipeline**

Исследование SWE-RPG проверяет всю цепочку:

`Requirements → Planning → Code`

Средний resolved rate протестированных coding agents — **31,5%**. Во многих конфигурациях **24,5–46% запусков ломались на восстановлении implicit requirements**.

Поэтому интереснее:

`Jira → Requirement Agent → Plan → Coding Agent → Verification`

и отдельно измерять:

`Requirement Recall / Plan Quality / Patch Quality`

⭐ **Практическая ценность:** 5/5  
🔥 **Стоит пробовать**

---

**3. Agent Plugins 1.0: Skills + MCP становятся переносимыми**

GitHub включил поддержку Agent Plugins 1.0 в VS Code, Copilot CLI, Copilot SDK и Copilot app.

Один package может содержать:

`Skill + MCP Server`

и использоваться совместимыми agent clients.

Для внутренних платформ это позволяет распространять `release-management`, `code-review`, `requirements-analysis`, `incident-analysis`, `embedded-cpp-review` как стандартные корпоративные capabilities.

⭐ **Практическая ценность:** 5/5  
📈 **Зрелость:** раннее внедрение

---

**4. Cursor начал относиться к environment агента как к CI artifact**

Cursor выпустил Builds для Cloud Agents:

`clone repo → install dependencies → setup → snapshot`

Cursor хранит:

`Build → commit SHA → logs → Agent Run`

Получается практически `Golden Environment for Agents`.

Для каждого запуска полезно сохранять:

`AgentRun + repository SHA + environment ID + toolchain + dependencies + model`

Тогда агентную задачу можно воспроизвести.

⭐ **Практическая ценность:** 5/5  
📈 **Зрелость:** можно применять сейчас

---

**5. Multi-Agent ≠ запустить 50 агентов на один repository**

Anthropic исследовала multi-agent systems.

Когда задача хорошо распараллеливается, swarm агентов может дать дополнительное покрытие. Но при совместном изменении связанного кода растут конфликты, зависимости и coordination overhead.

Полезнее:

`Coordinator → Task decomposition → isolated Worktrees → Verification → Merge`

То есть важнее:

**partitioning + ownership + isolation + merge gates**

⭐ **Практическая ценность:** 5/5  
🧪 **Зрелость:** раннее внедрение

---

**6. Shopify сделала тестовый API удобным для AI agents**

Mobile E2E tests Shopify деградировали примерно до **50% стабильности**.

Команда перепроектировала API: оставила маленький набор операций, сделала assertion обязательным после каждого action и использовала computer vision для взаимодействия с UI.

Результат — **98% test stability**.

Отсюда отличный принцип:

**не обучать агента пользоваться плохим API — сделать API таким, чтобы ошибиться было сложно**

Это применимо к:

`Testing API / Release API / Deployment API / Embedded tooling / MCP tools`

⭐ **Практическая ценность:** 5/5  
🔥 **Можно применять уже сейчас**

---

**💡 Что можно попробовать**

**1. Active Contract**

Перед Coding Agent собирать:

`Active Requirements + Superseded + Constraints + Acceptance Criteria`

вместо всей Jira history.

**2. Corporate Agent Plugins**

Упаковывать внутренние `Skills + MCP` в переносимые capability packages.

**3. Golden Agent Environment**

Версионировать:

`repo SHA + dependencies + toolchain + environment ID`

**4. Policy Gate**

Не полагаться только на `"не делай push в main"` в prompt.

Использовать:

`Agent → Policy → ALLOW / DENY / APPROVAL`

**5. Stage-aware Evals**

Измерять не только `Tests Passed`, но всю цепочку:

`Requirement Understanding → Plan → Context Retrieval → Code → Tests`

---

**Главный вывод недели**

Следующий этап AI Engineering выглядит уже не как:

`Developer → LLM → Code`

а скорее:

`Requirements → Active Contract → Context → Plan → Agents → Verification → Policy → Merge → Memory`

Гораздо важнее становятся:

**Specification + Context + Skills + Agent Environment + Policies + Verification + Memory + Evals**

---

**🔗 Почитать подробнее**

[SpecPath](https://arxiv.org/abs/2608.09799)

[SWE-RPG](https://arxiv.org/abs/2608.09072)

[Anthropic — Multiagent Systems](https://www.anthropic.com/research/multiagent-systems)

[GitHub — Agent Plugins 1.0](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/)

[Cursor — Cloud Agent Builds](https://cursor.com/changelog/08-13-26)

[Shopify — Mobile E2E Testing](https://shopify.engineering/mobile-e2e-testing)

[OpenAI — What’s New](https://learn.chatgpt.com/docs/whats-new)
