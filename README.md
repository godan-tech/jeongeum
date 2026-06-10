# Agent Brain Chip

> Run multiple specialized AI agents inside Discord — each with a persistent, markdown-only brain.

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

Agent Brain Chip solves this with a two-file brain per agent:

| File | Role |
|------|------|
| `SOUL.md` | Identity, personality, tone, hard limits |
| `SKILL.md` | Domain expertise, methods, workflows |
| `MEMORY.md` | Persistent decisions, preferences, history |
| `BRIDGE.md` | Reference paths, escalation rules |

Update the brain by editing markdown. No Python changes needed.

## Key Features

- **Multi-agent factory** — run 3+ specialized agents simultaneously via one `bot.py`
- **Markdown-only brain updates** — change agent behavior without touching code
- **Model-agnostic** — Claude CLI (subscription), Anthropic SDK (API key), or Ollama (free, local)
- **Auto-memory** — agents self-append to `MEMORY.md` via `[MEMORY_UPDATE: ...]` protocol
- **Shared context** — agents share conversation history for coherent multi-agent discussions
- **Zero additional cost** — leverages your existing Claude Pro subscription (Tier 1)

## Comparison

| | CrewAI / LangChain | llmcord | **Agent Brain Chip** |
|---|---|---|---|
| Brain update method | Python code | hardcoded | ✅ Markdown only |
| Multi-agent same server | ✅ | ❌ | ✅ |
| Model swap | code change | limited | ✅ One env var |
| Subscription leverage | ❌ requires API key | partial | ✅ Claude CLI |
| Setup complexity | high | medium | ✅ low |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/yourusername/agent-brain-chip
cd agent-brain-chip
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

| Backend | Cost | Setup | Notes |
|---------|------|-------|-------|
| Claude CLI (Tier 1) | $0 extra | existing Pro sub | policy gray area for automation |
| Anthropic SDK (Tier 2) | API usage | `ANTHROPIC_API_KEY` | recommended for production |
| Ollama local (Tier 3) | $0 | local hardware | M1 8GB+ recommended |
| Gemini CLI | $0 extra | existing sub | no policy restrictions |

Details → [docs/03-model-backends.md](docs/03-model-backends.md)

## License

MIT — fork freely, use commercially, attribution appreciated.
