"""Agent 2 — configure via .env"""
import os
from dotenv import load_dotenv
from bot import create_bot

load_dotenv()

client = create_bot(
    persona=f"{os.environ.get('AGENT2_NAME', 'Agent 2')} | {os.environ.get('AGENT2_ROLE', 'Creative Director')}",
    chip_dir=os.environ.get(
        "AGENT2_CHIP_DIR",
        os.path.join(os.path.dirname(__file__), "..", "chips", "agent2"),
    ),
    prefix=os.environ.get("AGENT2_SLASH", "/agent2"),
    bot_token=os.environ.get("AGENT2_TOKEN", ""),
    context_file=os.environ.get("CONTEXT_FILE", ""),
)

if __name__ == "__main__":
    client.run(os.environ["AGENT2_TOKEN"])
