# Chip System Deep Dive

## Why Chips?

Most multi-agent frameworks couple identity to code. To change a persona you edit Python, rebuild, redeploy.

Agent Brain Chip separates the two: `bot.py` handles Discord and AI calls — it never changes. Persona, expertise, and memory live in four markdown files. You can fully replace an agent's character by editing text.

## The Four Files

### SOUL.md — Identity

Sets **who the agent is** and **what it will not do**.

```markdown
## Who I Am
One short paragraph in first person.

## Communication Style
- Bullet list of how it speaks
- No filler phrases like "Certainly!"

## Hard Limits
- Will not do X
- Will not pretend to know Y
```

Keep it under 60 lines. Every constraint here is enforced on every message.

---

### SKILL.md — Methods

Sets **how the agent thinks through problems**.

```markdown
## Primary Methods

### [Method Name]
1. Step one
2. Step two
3. Step three

## Domain Expertise
- List areas it knows well

## Escalation Rules
- Type of request → which agent handles it
```

The step-by-step methods are the most valuable part. They turn a generic LLM into a specialist that approaches problems systematically.

---

### MEMORY.md — Persistent Context

Two sections:

**Standing context** — fill this in manually:
```markdown
## Standing Context
- Organization: Acme Corp
- Goal: Ship the mobile app by Q3
- Key constraint: Team of 3, no budget for external services
```

**Decisions log** — auto-appended by the agent at runtime:
```markdown
## Decisions Log
[2026-06-10] Chose PostgreSQL over SQLite — team already runs it in prod
[2026-06-11] Deferred mobile push notifications to v1.1
```

The MEMORY_UPDATE protocol: if the agent wants to remember something, it includes `[MEMORY_UPDATE: text]` in its reply. `bot.py` strips this from the visible output and appends the text to `MEMORY.md`.

---

### BRIDGE.md — References and Delegation

```markdown
## Reference Files
- Project roadmap: /path/to/roadmap.md  ← loaded on demand

## Delegation Rules
- Creative output → Agent 2
- Technical implementation → Agent 3
```

Reference files listed here are **not** loaded automatically — they're hints the agent can mention to the user ("check the roadmap"). If you want a file loaded automatically, add it to the chip loading order in `bot.py`.

---

## Prompt Architecture

The four chip files are assembled into the system prompt in this order:

```
[SOUL.md content]
[SKILL.md content]
[MEMORY.md content]
[BRIDGE.md content]
```

This block is the **stable prompt** — it's cached by the AI provider and only re-sent when one of the files changes.

On top of the stable prompt, each request adds a **volatile layer**:
```
[Shared context board — last N turns across all agents]
[Current message]
```

This split matters for cost: with Anthropic's prompt caching, the stable 4-file block is typically charged at 10% of normal input token cost after the first request.

---

## Shared Context Between Agents

When `SHARED_CONTEXT_PATH` is set, all agents write to a shared JSON file after each response. Each agent can see the last 10 turns from all agents in its volatile prompt.

This enables cross-agent continuity: if a user asks Agent 1 to brief Agent 3 on a decision, Agent 3 will see that conversation in its next request without any special routing.

The file uses file-level locking to prevent write conflicts when multiple agents process messages simultaneously.

---

## Token Budget Estimate

| Component | Approximate tokens |
|-----------|-------------------|
| SOUL.md (60 lines) | ~400 |
| SKILL.md (80 lines) | ~550 |
| MEMORY.md (40 lines) | ~300 |
| BRIDGE.md (20 lines) | ~150 |
| Shared context (10 turns) | ~1,500 |
| **Total system prompt** | **~2,900** |

With Anthropic cache: after the first request, ~2,900 tokens → ~290 cached tokens per request.

---

## Advanced: Context Board

Set `CONTEXT_FILE` in `.env` to a markdown file path. The contents are prepended to every request's volatile prompt. Use this for a live "situation board" — a file you update manually or via automation to inject the current project state into every agent's context.

```env
CONTEXT_FILE=/path/to/situation-board.md
```

Example `situation-board.md`:
```markdown
# Today's Focus
- Sprint ends Friday
- Deploy blocked by auth bug (Agent 3 owns)
- Client call at 3pm — prep needed (Agent 1 owns)
```
