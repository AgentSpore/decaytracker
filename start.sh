#!/bin/sh
set -e

# Start Next.js frontend (standalone mode) on port 3001
cd /app/frontend-standalone
PORT=3001 node server.js &

# Start FastAPI backend on port 8790
cd /app
exec uv run uvicorn decaytracker.main:app --host 0.0.0.0 --port 8790
