.PHONY: run dev test smoke build frontend clean

# Backend
run:
	uv run uvicorn decaytracker.main:app --host 0.0.0.0 --port 8790

dev:
	uv run uvicorn decaytracker.main:app --host 0.0.0.0 --port 8790 --reload

test:
	uv run pytest tests/ -v

smoke:
	uv run python smoke_test.py

# Frontend
frontend:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# Docker
build:
	docker build -t decaytracker .

# Research agent (manual trigger)
research:
	curl -s -X POST http://localhost:8790/api/research | python3 -m json.tool

# Clean
clean:
	rm -f /tmp/decaytracker.db
	rm -rf frontend/.next
