"""Agent 3 — configure via .env"""
import os
from dotenv import load_dotenv
from bot import create_bot

load_dotenv()

client = create_bot(
    persona=f"{os.environ.get('AGENT3_NAME', 'Agent 3')} | {os.environ.get('AGENT3_ROLE', 'Technical Lead')}",
    chip_dir=os.environ.get(
        "AGENT3_CHIP_DIR",
        os.path.join(os.path.dirname(__file__), "..", "chips", "agent3"),
    ),
    prefix=os.environ.get("AGENT3_SLASH", "/agent3"),
    bot_token=os.environ.get("AGENT3_TOKEN", ""),
    context_file=os.environ.get("CONTEXT_FILE", ""),
)

if __name__ == "__main__":
    client.run(os.environ["AGENT3_TOKEN"])
