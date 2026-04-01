#!/bin/sh
set -e

# Start FastAPI backend on internal port
cd /app
uv run uvicorn decaytracker.main:app --host 0.0.0.0 --port 8790 &

# Start Next.js frontend as main process (external port)
cd /app/frontend-standalone
export BACKEND_URL="http://localhost:8790"
export PORT="${PORT:-3000}"
exec node server.js
