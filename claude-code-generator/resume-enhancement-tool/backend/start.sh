#!/bin/bash
set -e

echo "Starting Resume Enhancement Tool Services..."

# Ensure workspace exists
mkdir -p workspace

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start Background Worker in background
# Redirect output to file for debugging
echo "Starting Background Worker..."
python worker.py > workspace/worker.log 2>&1 &

# Start API Server in foreground
echo "Starting API Server..."
# exec replaces the shell process, handling signals correctly
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
