# Model Backends

Set `MODEL_BACKEND` in `.env` to select the AI provider. Each agent can use a different backend.

## Comparison

| | Anthropic SDK | Gemini API | Ollama |
|---|---|---|---|
| **Cost** | Pay per token | Free tier available | Free (hardware cost) |
| **Setup** | API key | Free API key | Local model install |
| **Best for** | Production, Claude quality | Free legitimate automation | Privacy, offline |
| **Speed** | Fast | Fast | Depends on hardware |
| **Policy** | ✅ Approved | ✅ Approved | ✅ No restrictions |
| **Free tier** | ❌ | ✅ Rate-limited | ✅ Unlimited (local) |

---

## Anthropic SDK

```env
MODEL_BACKEND=anthropic-sdk
ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-haiku-4-5-20251001  # optional, defaults to haiku
```

Prompt caching is enabled automatically. The stable chip prompt is marked with `cache_control: ephemeral`, reducing cost on repeated requests by ~90%.

[Get an API key →](https://console.anthropic.com)

---

## Gemini API

The only **legitimately free API tier** that's officially approved for bot automation.

```env
MODEL_BACKEND=gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash   # or gemini-1.5-pro for higher quality
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com). No credit card required.

**Free tier limits (as of 2026):**
- Gemini 1.5 Flash: 15 requests/minute, 1 million tokens/day
- Gemini 1.5 Pro: 2 requests/minute, 50 requests/day

For most personal Discord servers this is sufficient. For high-traffic servers, the paid tier is available.

> Note: Unlike Claude subscriptions, Gemini API access is a separate product from Gemini Advanced. A free API key from AI Studio does not require a Google One subscription.

---

## Claude CLI (Not Recommended)

> ⚠️ **Terms of Service Warning**
>
> Claude CLI (Claude Code) is designed for individual interactive developer use. Running it as a subprocess to serve multiple Discord users through one subscription account likely violates Anthropic's Terms of Service — specifically the prohibition on automated access and account sharing.
>
> **Do not use this backend for any shared or public deployment.** For bots and automation, use the Anthropic SDK instead. If you choose to use it for private single-user experimentation, review [Anthropic's usage policies](https://www.anthropic.com/legal/aup) first.

```env
MODEL_BACKEND=claude-cli
CLAUDE_BIN=/path/to/claude   # find it: which claude
```

`CLAUDE_BIN_DIR` can be set instead of `CLAUDE_BIN` if you want to specify just the directory.

---

## Ollama

```env
MODEL_BACKEND=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

Ollama runs models locally. No data leaves your machine. No per-request cost.

**Minimum hardware for good results:**
- Apple Silicon (M1/M2/M3): 16GB unified memory → llama3 8B runs well
- NVIDIA GPU: 8GB VRAM → llama3 8B, 16GB → llama3 70B (quantized)
- CPU only: works but expect 10-30 second response times

Popular models for Discord bots:
```bash
ollama pull llama3          # 8B, good balance
ollama pull mistral         # 7B, fast
ollama pull llama3:70b      # 70B, best quality (needs 40GB+ RAM)
```

Ollama can also be run on a remote server — just set `OLLAMA_HOST` to that server's address.

---

## Mixing Backends

Each agent file reads `MODEL_BACKEND` from the environment at startup. You can run different agents with different backends by using shell scripts:

```bash
# start_agents.sh example
MODEL_BACKEND=anthropic-sdk python agents/agent1.py &
MODEL_BACKEND=ollama OLLAMA_MODEL=llama3 python agents/agent2.py &
```

Or use separate `.env` files per agent and load them explicitly in each `agents/agentN.py`.
