# Chip Authoring Guide

Each agent is defined by four markdown files — its **Brain Chip**.

```
chips/
└── agent1/
    ├── SOUL.md     ← personality, tone, hard limits
    ├── SKILL.md    ← methods, frameworks, domain expertise
    ├── MEMORY.md   ← persistent context + decisions log
    └── BRIDGE.md   ← reference files + delegation rules
```

## File Purposes

| File | What to put here | When it's loaded |
|------|-----------------|-----------------|
| `SOUL.md` | Who the agent is, how it communicates, what it refuses | Every request |
| `SKILL.md` | Step-by-step methods, domain knowledge, escalation rules | Every request |
| `MEMORY.md` | Standing context (org, project, stack) + auto-appended decisions | Every request |
| `BRIDGE.md` | External file references, which agent handles what | Every request |

All four files are concatenated into the system prompt on every request. Keep them focused and short — under 300 lines total is the target.

## Creating a New Agent

1. Copy `chips/agent1/` to a new folder:
   ```
   cp -r chips/agent1 chips/myagent
   ```

2. Edit the four files to match your use case.

3. Add to `.env`:
   ```
   AGENT1_NAME=Mira
   AGENT1_ROLE=Research Lead
   AGENT1_CHIP_DIR=chips/myagent
   AGENT1_SLASH=/mira
   ```

4. Start the agent:
   ```
   python agents/agent1.py
   ```

## The MEMORY_UPDATE Protocol

When a decision is worth remembering, an agent can append it to its own `MEMORY.md` automatically. In the response, include a line like:

```
[MEMORY_UPDATE: Decided to use PostgreSQL over SQLite because the team already runs it in production]
```

The bot engine strips this from the visible reply and appends it to `MEMORY.md`. The next conversation starts with this context already loaded.

## Tips

- **SOUL.md** sets the ceiling. If the agent routinely does things you don't want, add a Hard Limit here.
- **SKILL.md** sets the floor. If responses feel shallow, add a method or expand domain expertise.
- **MEMORY.md** is the only file the agent can write to. Everything else is read-only at runtime.
- **BRIDGE.md** delegation rules are social contracts between agents — they only work if both agents' SOUL.md files agree on the boundary.
