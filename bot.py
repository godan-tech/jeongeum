"""
Agent Brain Chip — Core Factory
================================
Creates a Discord bot that loads its "brain" from markdown chip files.
One factory, any number of agents.

Usage:
    from bot import create_bot
    client = create_bot(
        persona="Agent 1 | Strategic Advisor",
        chip_dir="./chips/agent1",
        prefix="/agent1",
        bot_token=os.environ["AGENT1_TOKEN"],
    )
    client.run(os.environ["AGENT1_TOKEN"])
"""

import asyncio
import subprocess
import discord
from discord import app_commands
from collections import deque
import json
import os
import re
import datetime
import fcntl

# ── Shared context (inter-agent conversation history) ──────────────────────
SHARED_CONTEXT_PATH = os.environ.get(
    "SHARED_CONTEXT_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared_context.json"),
)
_CONTEXT_LOCK_PATH = SHARED_CONTEXT_PATH + ".lock"


def _append_shared_context(speaker: str, message: str) -> None:
    try:
        msg_str = str(message)
        if len(msg_str) > 300:
            msg_str = msg_str[:280] + "... (truncated)"

        with open(_CONTEXT_LOCK_PATH, "w") as lock_fd:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            try:
                history = []
                if os.path.exists(SHARED_CONTEXT_PATH):
                    with open(SHARED_CONTEXT_PATH, "r", encoding="utf-8") as f:
                        history = json.load(f)
                history.append({"speaker": speaker, "message": msg_str})
                history = history[-10:]
                tmp = SHARED_CONTEXT_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                os.replace(tmp, SHARED_CONTEXT_PATH)
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
    except Exception as e:
        print(f"[Context Error] {e}", flush=True)


def _get_shared_context_str() -> str:
    try:
        if not os.path.exists(SHARED_CONTEXT_PATH):
            return "No recent history."
        with open(SHARED_CONTEXT_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
        return "\n".join(f"- **{e['speaker']}**: {e['message']}" for e in history)
    except Exception as e:
        return f"Error reading history: {e}"


# ── Bot factory ────────────────────────────────────────────────────────────

def create_bot(*, persona: str, chip_dir: str, prefix: str, bot_token: str,
               context_file: str = ""):
    """
    Create a Discord bot with a Brain Chip personality.

    Args:
        persona:      Display name + role, e.g. "Agent 1 | Strategic Advisor"
        chip_dir:     Path to folder containing SOUL.md / SKILL.md / MEMORY.md / BRIDGE.md
        prefix:       Slash command name, e.g. "/agent1"
        bot_token:    Discord bot token
        context_file: Optional path to a markdown file injected as live context
    """
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    processed_ids = deque(maxlen=500)
    replied_ids = deque(maxlen=500)
    slash_ids = deque(maxlen=500)
    ready_at = [None]

    def _load_file(path: str) -> str:
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _extract_and_save_memory(response: str) -> str:
        """Extract [MEMORY_UPDATE: ...] tags, append to MEMORY.md, return clean response."""
        pattern = r'\[MEMORY_UPDATE:\s*(.*?)\]'
        matches = re.findall(pattern, response, re.DOTALL)
        if not matches:
            return response
        today = datetime.date.today().strftime("%Y-%m-%d")
        memory_path = os.path.join(chip_dir, "MEMORY.md")
        entries = [
            f"\n---\n**[{today}] Auto-saved — {persona}**\n{m.strip()}\n"
            for m in matches
        ]
        try:
            with open(memory_path, "a", encoding="utf-8") as f:
                f.write("".join(entries))
            print(f"[{persona}] MEMORY_UPDATE saved ({len(matches)} entries)", flush=True)
        except Exception as e:
            print(f"[{persona}] MEMORY_UPDATE failed: {e}", flush=True)
        return re.sub(pattern, "", response, flags=re.DOTALL).strip()

    def _build_stable_prompt() -> str:
        """Cache-friendly: identity + chip files. Changes rarely."""
        parts = [f"""\
## [Agent Identity — Read First]

You are **{persona}**.
- Introduce yourself only as "{persona}"
- Never reveal the underlying AI model or tool names
- Load SOUL → SKILL → MEMORY → BRIDGE in order; SOUL defines your personality absolutely
---"""]

        for fname, label in [
            ("SOUL.md",   "Core Identity (SOUL)"),
            ("SKILL.md",  "Methods & Expertise (SKILL)"),
            ("MEMORY.md", "Persistent Memory (MEMORY)"),
            ("BRIDGE.md", "References & Delegation (BRIDGE)"),
        ]:
            content = _load_file(os.path.join(chip_dir, fname))
            if content:
                parts.append(f"\n\n## {label}\n{content}")

        parts.append("""\n\n## [Auto Memory Protocol]
Append `[MEMORY_UPDATE: one-line summary]` at the end of your response ONLY when:
- The user makes an explicit decision or states a clear preference
- An important constraint is confirmed
- The same topic recurs 3+ times

Do NOT append for routine Q&A or already-recorded items.""")

        return "\n".join(parts)

    def _build_volatile_prompt() -> str:
        """Refreshed every call: optional context board + shared history."""
        parts = []

        if context_file and os.path.exists(context_file):
            content = _load_file(context_file)
            if content:
                parts.append(
                    f"## [Live Context Board]\n```markdown\n{content}\n```"
                )

        shared = _get_shared_context_str()
        parts.append(
            f"## [Recent Conversation History]\n"
            f"Stay consistent with prior messages from other agents and the user.\n"
            f"```markdown\n{shared}\n```"
        )

        return "\n\n".join(parts)

    async def _run_agent_async(prompt: str) -> str:
        system = _build_stable_prompt() + "\n\n" + _build_volatile_prompt()

        env = dict(os.environ)
        home = os.environ.get("HOME", os.path.expanduser("~"))
        env["HOME"] = home
        extra_bin = os.environ.get("CLAUDE_BIN_DIR", "")
        path_prefix = extra_bin + ":" if extra_bin else ""
        env["PATH"] = path_prefix + "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

        # ── Model backend selection ──────────────────────────────────────
        backend = os.environ.get("MODEL_BACKEND", "claude-cli").lower()

        if backend == "anthropic-sdk":
            return await _run_via_sdk(prompt, system)
        elif backend == "gemini":
            return await _run_via_gemini(prompt, system)
        elif backend == "ollama":
            return await _run_via_ollama(prompt, system, env)
        else:
            return await _run_via_claude_cli(prompt, system, env)

    async def _run_via_claude_cli(prompt: str, system: str, env: dict) -> str:
        """Tier 1: Claude CLI subprocess (requires `claude` installed + logged in)."""
        default_bin = os.path.join(
            os.environ.get("HOME", os.path.expanduser("~")), ".local/bin/claude"
        )
        claude_bin = os.environ.get("CLAUDE_BIN", default_bin)
        if not os.path.exists(claude_bin):
            claude_bin = "claude"

        cmd = [claude_bin, "-p", prompt, "--system-prompt", system, "--tools", ""]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except Exception:
                    pass
                return "Response timeout (120s)"
            if proc.returncode != 0:
                return f"CLI error:\n{stderr.decode('utf-8', errors='replace')[:500]}"
            return stdout.decode("utf-8", errors="replace").strip() or "No response"
        except Exception as e:
            return f"CLI execution error: {e}"

    async def _run_via_sdk(prompt: str, system: str) -> str:
        """Tier 2: Anthropic Python SDK with prompt caching (requires ANTHROPIC_API_KEY)."""
        try:
            import anthropic
            ac = anthropic.AsyncAnthropic()
            model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
            resp = await ac.messages.create(
                model=model,
                max_tokens=2048,
                system=[
                    {"type": "text", "text": _build_stable_prompt(),
                     "cache_control": {"type": "ephemeral"}},
                    {"type": "text", "text": _build_volatile_prompt()},
                ],
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        except Exception as e:
            return f"SDK error: {e}"

    async def _run_via_gemini(prompt: str, system: str) -> str:
        """Gemini API — free tier available, approved for automation."""
        try:
            import aiohttp
            api_key = os.environ.get("GEMINI_API_KEY", "")
            model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"parts": [{"text": prompt}]}],
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    data = await resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini error: {e}"

    async def _run_via_ollama(prompt: str, system: str, env: dict) -> str:
        """Tier 3: Ollama local model (requires ollama running locally)."""
        try:
            import aiohttp
            host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            model = os.environ.get("OLLAMA_MODEL", "llama3.2")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{host}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    data = await resp.json()
                    return data.get("message", {}).get("content", "No response")
        except Exception as e:
            return f"Ollama error: {e}"

    # ── Slash command ──────────────────────────────────────────────────────
    cmd_name = prefix.lstrip("/")

    @tree.command(name=cmd_name, description=f"Ask {persona}")
    @app_commands.describe(message="Your message")
    async def slash_cmd(interaction: discord.Interaction, message: str):
        if interaction.id in slash_ids:
            return
        slash_ids.append(interaction.id)
        await interaction.response.defer()

        _append_shared_context("User", f"/{cmd_name} {message}")
        response = await _run_agent_async(message)
        response = _extract_and_save_memory(response)
        _append_shared_context(persona, response)

        if len(response) <= 2000:
            await interaction.followup.send(response)
        else:
            for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                await interaction.followup.send(chunk)

    @tree.command(name="remember", description=f"Save to {persona}'s memory")
    @app_commands.describe(content="What to remember")
    async def remember_cmd(interaction: discord.Interaction, content: str):
        today = datetime.date.today().strftime("%Y-%m-%d")
        memory_path = os.path.join(chip_dir, "MEMORY.md")
        entry = f"\n---\n**[{today}] Manual save**\n{content}\n"
        try:
            with open(memory_path, "a", encoding="utf-8") as f:
                f.write(entry)
            await interaction.response.send_message(
                f"Saved to **{persona}**'s memory:\n> {content}", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"Save failed: {e}", ephemeral=True)

    # ── Gateway events ─────────────────────────────────────────────────────
    @client.event
    async def on_ready():
        ready_at[0] = discord.utils.utcnow()
        for guild in client.guilds:
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
        print(f"{persona} online: {client.user} ({len(client.guilds)} servers)", flush=True)

    @client.event
    async def on_message(message):
        if message.author.id == client.user.id:
            return
        if message.author.bot:
            return
        if message.interaction_metadata is not None:
            return
        if ready_at[0] and message.created_at < ready_at[0]:
            return

        content = message.content.strip()
        is_mention = client.user in message.mentions
        is_prefix = content == prefix or content.startswith(prefix + " ")
        if not (is_mention or is_prefix):
            return

        if message.id in processed_ids:
            return
        processed_ids.append(message.id)

        prompt = (
            content.replace(f"<@{client.user.id}>", "").strip()
            if is_mention
            else content[len(prefix):].strip()
        )
        if not prompt:
            await message.reply("How can I help?")
            return

        _append_shared_context("User", f"@{persona} {prompt}")
        async with message.channel.typing():
            response = await _run_agent_async(prompt)
        response = _extract_and_save_memory(response)
        _append_shared_context(persona, response)

        if message.id in replied_ids:
            return
        replied_ids.append(message.id)

        if len(response) <= 2000:
            await message.reply(response, mention_author=False)
        else:
            chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.reply(chunk, mention_author=False)
                else:
                    await message.channel.send(chunk)

    return client
