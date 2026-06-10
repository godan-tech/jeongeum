# Jeongeum (정음)

> A personal multi-agent Discord setup — built from scratch to solve the cold-start problem.

Named after 훈민정음 (Hunminjeongeum) — the writing system designed so *anyone* could express *any* thought. Jeongeum applies that idea to AI agents: any persona, expressible in four plain-text files.

Cloning an existing framework is easy. The hard part is shaping it to your actual work. This repo is a direct attempt at that — a minimal, self-contained setup I built and use, open-sourced so others can adapt it to their own context.

---

## What I was trying to solve

### 1. Agents that actually remember

The cold-start problem: every session starts from scratch. You re-explain your business context, preferences, and past decisions — every time.

The fix here is a self-writing memory protocol. When an agent decides something worth keeping, it appends a tag to its response:

```
[MEMORY_UPDATE: client prefers bullet-point summaries over prose]
```

`bot.py` strips the tag and appends the line to `MEMORY.md`. No vector store. No external server. Just a file append — and the agent reads it back next time.

### 2. A setup you can fully own in ~400 lines

Frameworks solve general problems and carry that weight. This is a template — one `bot.py` file that runs as many Discord agents as you want, each with its own persona and memory, configurable without touching Python.

```
chips/
├── agent1/
│   ├── SOUL.md    ← who the agent is
│   ├── SKILL.md   ← what it knows
│   ├── MEMORY.md  ← what it remembers
│   └── BRIDGE.md  ← who else to involve
└── agent2/
    └── ...
```

To change an agent's identity: edit the markdown. To add an agent: copy a folder and add one line to your startup script.

---

## Quick Start

```bash
git clone https://github.com/godan-tech/jeongeum
cd jeongeum
pip install -r requirements.txt

cp .env.example .env
# Add: AGENT1_TOKEN, MODEL_BACKEND, ANTHROPIC_API_KEY (or GEMINI_API_KEY)

python agents/agent1.py
```

Full setup guide → [docs/01-quickstart.md](docs/01-quickstart.md)

---

## Model backends

| Backend | Cost | How |
|---------|------|-----|
| **Anthropic SDK** | Pay per token | `MODEL_BACKEND=anthropic-sdk` + API key |
| **Gemini API** | Free tier (15 req/min) | `MODEL_BACKEND=gemini` + free AI Studio key |
| **Ollama** | Free (local) | `MODEL_BACKEND=ollama` + local hardware |

Prompt caching enabled automatically for Anthropic SDK: stable chip files are marked `cache_control: ephemeral`, reducing repeat-call cost ~90%.

> **Claude CLI note:** Running Claude CLI as a subprocess to serve multiple Discord users likely violates Anthropic's Terms of Service. Use the Anthropic SDK for bots. See [docs/03-model-backends.md](docs/03-model-backends.md).

---

## What this borrows from

| Project | What we took |
|---------|-------------|
| [llmcord](https://github.com/jakobdylanc/llmcord) | Discord + LLM bot skeleton |
| [MemGPT / Letta](https://github.com/letta-ai/letta) | Concept of agent self-memory; simplified to file-append instead of a memory server |
| [OpenPersona](https://github.com/acnlabs/OpenPersona) | SOUL.md file-based persona concept |
| [Semantic Kernel](https://github.com/microsoft/semantic-kernel) | Skills-as-files pattern |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Role-based multi-agent mental model |

---

## Architecture

```
Discord message
      │
      ▼
bot.py  ← thin gateway (zero domain knowledge)
      │
      ├── stable prompt: SOUL + SKILL + MEMORY + BRIDGE  ← cached
      └── volatile prompt: shared history + live context  ← refreshed per call
      │
      ▼
LLM (Anthropic / Gemini / Ollama)
      │
      ▼
Response → strip [MEMORY_UPDATE] → append to MEMORY.md → send to Discord
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design details.

---

## License

MIT — fork freely, use commercially, attribution appreciated.
