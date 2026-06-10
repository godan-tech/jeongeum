# Quickstart: Deploy Your First Agent in 15 Minutes

## Prerequisites

- Python 3.10+
- A Discord account with Developer Portal access
- One of: Anthropic API key, Claude CLI installed, or Ollama running locally

---

## Step 1: Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → give it a name (e.g. "Agent 1")
3. Go to **Bot** → click **Add Bot**
4. Under **Privileged Gateway Intents**, enable:
   - Server Members Intent
   - Message Content Intent
5. Copy the **Token** — you'll need it for `.env`
6. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`
7. Open the generated URL in a browser and invite the bot to your server

Repeat for each agent you want to run.

---

## Step 2: Set Up API Access

Choose **one** backend per agent.

### Option A: Anthropic SDK (Recommended)

Best for production use. Pay-per-token, no hardware requirements.

1. Get an API key at [console.anthropic.com](https://console.anthropic.com)
2. Add to `.env`:
   ```
   MODEL_BACKEND=anthropic-sdk
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Option B: Ollama (Free, Local)

No API costs. Requires a machine with 8GB+ VRAM (or 16GB+ unified memory for Apple Silicon).

1. Install Ollama: [ollama.com](https://ollama.com)
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
3. Add to `.env`:
   ```
   MODEL_BACKEND=ollama
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

### Option C: Claude CLI

For personal use if you have an active Claude subscription (Pro or Max). See [policy note](../README.md#model-backends) before using this in production.

1. Install Claude CLI: [docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code)
2. Run `claude` once to authenticate via OAuth
3. Add to `.env`:
   ```
   MODEL_BACKEND=claude-cli
   CLAUDE_BIN=/path/to/claude   # find it: which claude
   ```

---

## Step 3: Configure .env

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:

```env
# Agent 1
AGENT1_TOKEN=your_discord_bot_token_here
AGENT1_NAME=Alex
AGENT1_ROLE=Strategic Advisor

# Model backend (pick one from Step 2)
MODEL_BACKEND=anthropic-sdk
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5: Start the Agents

**Single agent:**
```bash
python agents/agent1.py
```

**All agents at once:**
```bash
bash start_agents.sh
```

---

## Step 6: Test in Discord

In your Discord server, type:
```
/agent1 What are your top priorities today?
```

The bot should respond within a few seconds.

---

## Customizing the Persona

The agent's personality, expertise, and memory live in `chips/agent1/`. Edit the four files:

- `SOUL.md` — who the agent is and how it speaks
- `SKILL.md` — what methods and domains it knows
- `MEMORY.md` — standing context (organization, project, constraints)
- `BRIDGE.md` — which other agents to delegate to

See the [Chip Authoring Guide](../chips/README.md) for details.

---

## Troubleshooting

**Bot doesn't respond to slash commands**
→ Wait 1-2 minutes after inviting — Discord takes time to register commands globally.
→ Make sure Message Content Intent is enabled in the Developer Portal.

**`AGENT1_TOKEN` env var missing error**
→ Check that your `.env` file is in the project root and `python-dotenv` is installed.

**Ollama connection refused**
→ Make sure Ollama is running: `ollama serve`
→ Check `OLLAMA_HOST` matches where Ollama is listening (default: `http://localhost:11434`)

**Rate limit errors from Discord**
→ The bot includes exponential backoff retry logic. If you see persistent 429s, you may have multiple bot instances running — check with `ps aux | grep python`.
