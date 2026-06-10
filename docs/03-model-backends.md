# Model Backends

Set `MODEL_BACKEND` in `.env` to select the AI provider. Each agent can use a different backend.

## Comparison

| | Anthropic SDK | Claude CLI | Ollama |
|---|---|---|---|
| **Cost** | Pay per token | Included in subscription | Free (hardware cost) |
| **Setup** | API key only | CLI install + OAuth | Local model install |
| **Best for** | Production, teams | Personal use | Privacy, offline |
| **Speed** | Fast | Medium | Depends on hardware |
| **Policy** | ✅ Approved for automation | ⚠️ Gray area for bots | ✅ No restrictions |
| **Model quality** | Claude Sonnet/Haiku | Claude (subscription tier) | Varies by model |

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

## Claude CLI

```env
MODEL_BACKEND=claude-cli
CLAUDE_BIN=/path/to/claude   # find it: which claude
```

Uses your existing Claude subscription via OAuth. No API costs beyond the subscription.

**Policy note:** Anthropic's terms are written for interactive use. Running Claude CLI in an automated bot is a gray area. Suitable for personal projects and experimentation. For anything shared or production, use the SDK.

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
