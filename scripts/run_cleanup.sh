#!/bin/bash
# VBoarder Log Rotation and Cleanup - Cron Setup
#
# Add this to crontab to run daily at 2 AM:
# crontab -e
# Add line: 0 2 * * * /path/to/vboarder/scripts/run_cleanup.sh >> /path/to/vboarder/logs/cleanup.log 2>&1

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run the cleanup script
echo "============================================================"
echo "Running VBoarder cleanup at $(date)"
echo "============================================================"

python3 "$SCRIPT_DIR/cleanup_logs_memory.py"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Cleanup completed successfully"
else
    echo "❌ Cleanup failed with exit code $EXIT_CODE"
fi

echo ""
