# Architecture

## Core Principle: Thin Gateway, Rich Chips

`bot.py` is a thin gateway. It handles:
- Discord slash command registration and routing
- Deferring responses to beat the 3-second timeout
- Assembling the system prompt from chip files
- Dispatching to the selected model backend
- Parsing and applying MEMORY_UPDATE tags
- Writing to shared context

`bot.py` contains zero domain knowledge, zero persona, zero memory. All intelligence lives in the four chip files.

## Prompt Architecture

```
┌─────────────────────────────────────┐
│           STABLE PROMPT             │  ← Cache target
│                                     │
│  SOUL.md   (identity)               │
│  SKILL.md  (methods)                │
│  MEMORY.md (context + decisions)    │
│  BRIDGE.md (delegation rules)       │
│                                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│           VOLATILE PROMPT           │  ← Rebuilt per request
│                                     │
│  Context board (CONTEXT_FILE)       │
│  Shared history (last N turns)      │
│  Current user message               │
│                                     │
└─────────────────────────────────────┘
```

The stable/volatile split enables prompt caching. On Anthropic SDK, the stable block is marked `cache_control: ephemeral`. After the first request, the 4-file block costs ~10% of normal input tokens.

## Model Backend Tiers

```
Tier 1: Claude CLI subprocess
  → subprocess("claude -p ...", stdin=prompt)
  → Uses OAuth subscription
  → No per-token cost / policy gray area

Tier 2: Anthropic SDK  (recommended)
  → anthropic.AsyncAnthropic().messages.create(...)
  → API key, pay per token
  → Prompt cache enabled

Tier 3: Ollama  (local)
  → aiohttp POST to /api/generate
  → No API cost, hardware required
  → Full privacy, works offline
```

`MODEL_BACKEND` env var selects the tier. All three tiers receive identical prompt content.

## Shared Context Protocol

```
Agent 1 ──write──► shared_context.json ◄──read── Agent 2
Agent 2 ──write──► shared_context.json ◄──read── Agent 3
                         │
                    file lock
                    (prevents simultaneous writes)
```

Each write appends `{role, name, content, timestamp}` and trims to the last N turns. Every agent reads the full log on each request and injects it into the volatile prompt.

## MEMORY_UPDATE Protocol

```
User message ──► Agent responds
                      │
                      ├─ Visible reply (MEMORY_UPDATE tag stripped)
                      │
                      └─ [MEMORY_UPDATE: decision text]
                                │
                           Appended to
                           chips/agentN/MEMORY.md
```

The agent can self-update its own persistent memory without any external system. On the next request, MEMORY.md is re-loaded as part of the stable prompt.

## Duplicate Prevention

Two `deque(maxlen=20)` track recently processed interaction IDs and message IDs per bot instance. Any interaction or message seen within the last 20 entries is dropped silently. This prevents double-processing under Discord's at-least-once delivery guarantee.

## File Structure

```
agent-brain-chip/
├── bot.py                  ← Core engine (don't edit for persona changes)
├── agents/
│   ├── agent1.py           ← create_bot() call, reads env
│   ├── agent2.py
│   └── agent3.py
├── chips/
│   ├── README.md           ← Chip authoring guide
│   └── agentN/
│       ├── SOUL.md
│       ├── SKILL.md
│       ├── MEMORY.md       ← Runtime-writable
│       └── BRIDGE.md
├── docs/
│   ├── 01-quickstart.md
│   ├── 02-chip-guide.md
│   └── 03-model-backends.md
├── start_agents.sh
├── requirements.txt
├── .env.example
└── .gitignore
```

## Design Decisions

**Why not LangChain or CrewAI?**
Those frameworks are powerful for complex pipelines but require significant Python to configure personality. Agent Brain Chip optimizes for a different goal: make persona as easy to change as a text file, and make the engine invisible.

**Why Discord slash commands instead of message commands?**
Slash commands give built-in command documentation, argument validation, and avoid the need to mention the bot. The `defer()` pattern solves the 3-second acknowledgment requirement.

**Why file-based shared context instead of a database?**
Eliminates infrastructure requirements. SQLite would be the next step for high-throughput scenarios, but for typical Discord server traffic (< 100 requests/hour), file-with-lock is sufficient and requires no setup.

**Why load all four chip files on every request?**
To keep the architecture simple and ensure the agent always has its full identity. With prompt caching, the cost is negligible after the first request. The alternative (lazy loading) adds complexity without meaningful savings.
