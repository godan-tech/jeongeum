#!/usr/bin/env bash
# Start all agents. Each runs in the background.
# Logs go to logs/agentN.log

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

cd "$SCRIPT_DIR"

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Starting Agent 1..."
python agents/agent1.py > "$LOG_DIR/agent1.log" 2>&1 &
echo "  PID: $!"

echo "Starting Agent 2..."
python agents/agent2.py > "$LOG_DIR/agent2.log" 2>&1 &
echo "  PID: $!"

echo "Starting Agent 3..."
python agents/agent3.py > "$LOG_DIR/agent3.log" 2>&1 &
echo "  PID: $!"

echo ""
echo "All agents running. Logs in $LOG_DIR/"
echo "To stop all agents: pkill -f 'python agents/'"
