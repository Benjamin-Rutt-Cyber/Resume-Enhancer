#!/bin/bash
set -e

echo "Starting Resume Enhancement Tool Services..."

# Start Background Worker in background
# Redirect output to stdout/stderr for logging
echo "Starting Background Worker..."
python worker.py &

# Start API Server in foreground
echo "Starting API Server..."
# exec replaces the shell process, handling signals correctly
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
