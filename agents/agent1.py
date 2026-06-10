"""Agent 1 — configure via .env"""
import os
from dotenv import load_dotenv
from bot import create_bot

load_dotenv()

client = create_bot(
    persona=f"{os.environ.get('AGENT1_NAME', 'Agent 1')} | {os.environ.get('AGENT1_ROLE', 'Strategic Advisor')}",
    chip_dir=os.environ.get(
        "AGENT1_CHIP_DIR",
        os.path.join(os.path.dirname(__file__), "..", "chips", "agent1"),
    ),
    prefix=os.environ.get("AGENT1_SLASH", "/agent1"),
    bot_token=os.environ.get("AGENT1_TOKEN", ""),
    context_file=os.environ.get("CONTEXT_FILE", ""),
)

if __name__ == "__main__":
    client.run(os.environ["AGENT1_TOKEN"])
