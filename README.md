# Jeongeum (정음)

> Run multiple specialized AI agents inside Discord — each with a persistent, markdown-only brain.

Named after 훈민정음 (Hunminjeongeum) — the writing system Sejong the Great created so *anyone* could express *any* thought. Jeongeum does the same for AI agents: any persona, any expertise, expressed through four markdown files.

```
Discord message
      │
      ▼
bot.py  ← thin gateway (no AI logic)
      │  subprocess / SDK call
      ▼
[SOUL] + [SKILL] + [MEMORY] + [BRIDGE]  ← the Brain Chip
      │
      ▼
Response to Discord channel
```

## Why

Every AI session starts from scratch. You repeat your business context, tone guidelines, and past decisions on every new conversation — a silent productivity tax called the **Cold Start Problem**.

Jeongeum solves this with a four-file brain per agent:

| File | Role |
|------|------|
| `SOUL.md` | Identity, personality, tone, hard limits |
| `SKILL.md` | Domain expertise, methods, workflows |
| `MEMORY.md` | Persistent decisions, preferences, history |
| `BRIDGE.md` | Reference paths, escalation rules |

Update the brain by editing markdown. No Python changes needed.

## Key Features

- **Multi-agent factory** — run 3+ specialized agents simultaneously via one `bot.py`
- **Markdown-only brain** — change agent persona, expertise, and memory without touching code
- **Model-agnostic** — Anthropic SDK or Ollama; swap via one env var
- **Auto-memory** — agents self-append decisions to `MEMORY.md` via `[MEMORY_UPDATE: ...]`
- **Shared context** — agents share conversation history across a Discord server
- **Prompt cache optimized** — stable chip block cached; ~90% token reduction on repeated calls

## What's Original

Most agent frameworks (CrewAI, MetaGPT, LangChain) require Python to define who an agent *is*. Jeongeum separates identity from code entirely:

- **Four-file Brain Chip** — SOUL / SKILL / MEMORY / BRIDGE as the complete agent spec. Swap the files, swap the agent. No Python changes.
- **MEMORY_UPDATE protocol** — agents self-write to their own `MEMORY.md` via inline tags. Persistent memory without a database or external system.
- **Stable/volatile prompt split** — chip files form a cache-stable block; per-request context stays volatile. Reduces token cost ~90% on repeated calls via Anthropic prompt caching.
- **Thin gateway principle** — `bot.py` contains zero domain knowledge. All intelligence lives in markdown.

## Inspired By

Jeongeum stands on the shoulders of these projects:

| Project | What we borrowed | What we changed |
|---------|-----------------|-----------------|
| [CrewAI](https://github.com/crewAIInc/crewAI) | Role-based multi-agent concept | Removed Python for role definition → markdown only |
| [llmcord](https://github.com/jakobdylanc/llmcord) | Discord + LLM bot pattern | Added multi-agent factory, persistent memory, model-agnostic backend |
| [MemGPT / Letta](https://github.com/letta-ai/letta) | Agent self-memory concept | Simplified to inline tag protocol, no external memory server |
| [Open Interpreter](https://github.com/OpenInterpreter/open-interpreter) | "LLMs as practical tools" philosophy | Applied to Discord context with persona persistence |
| [LangChain](https://github.com/langchain-ai/langchain) | Model abstraction layer idea | Reduced to 3 env-var-selectable backends, no chain DSL |

## Comparison

| | CrewAI / LangChain | llmcord | **Jeongeum** |
|---|---|---|---|
| Brain update method | Python code | hardcoded | ✅ Markdown only |
| Multi-agent same server | ✅ | ❌ | ✅ |
| Model swap | code change | limited | ✅ One env var |
| Persistent memory | external DB | ❌ | ✅ Self-write protocol |
| Setup complexity | high | medium | ✅ low |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/yourusername/jeongeum
cd jeongeum
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — add Discord bot tokens and model config

# 3. Customize your agent's brain
# Edit chips/agent1/SOUL.md, SKILL.md, MEMORY.md

# 4. Run
python agents/agent1.py
```

Full setup guide → [docs/01-quickstart.md](docs/01-quickstart.md)

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for design principles, Tier evolution path, and the chip system specification.

## Supported Model Backends

| Backend | Cost | Setup | Recommended for |
|---------|------|-------|----------------|
| **Anthropic SDK** | API usage | `ANTHROPIC_API_KEY` | Production, teams |
| **Ollama** | Free | local hardware (8GB+ VRAM) | Privacy, offline, zero API cost |

> **Note on Claude CLI:** Running Claude CLI as a subprocess in an automated bot is outside the intended use of Claude's interactive subscription plans and may conflict with Anthropic's Terms of Service, particularly when serving multiple end users. This project does not recommend or support that pattern for shared or production use. See [docs/03-model-backends.md](docs/03-model-backends.md) for details.

Details → [docs/03-model-backends.md](docs/03-model-backends.md)

## License

MIT — fork freely, use commercially, attribution appreciated.
