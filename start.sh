#!/bin/sh
set -e

# Start Next.js frontend (standalone mode)
cd /app/frontend-standalone
node server.js &

# Start FastAPI backend
cd /app
exec uv run uvicorn decaytracker.main:app --host 0.0.0.0 --port ${PORT:-8790}
