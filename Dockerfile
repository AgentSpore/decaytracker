# ── Stage 1: Frontend build ──
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

# ── Stage 2: Backend + serve frontend ──
FROM python:3.12-slim

# System deps for Playwright (chromium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg \
    libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 libcups2 \
    libxss1 libgtk-3-0 libxshmfence1 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Python deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Install Playwright browsers
RUN uv run playwright install chromium

# Backend source
COPY src/ src/

# Frontend static build
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend-standalone
COPY --from=frontend-builder /app/frontend/.next/static ./frontend-standalone/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend-standalone/public

# Startup script
COPY start.sh ./
RUN chmod +x start.sh

ENV PORT=3000
ENV DB_PATH=/data/decaytracker.db
ENV NODE_ENV=production

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD curl -f http://localhost:8790/health || exit 1

CMD ["./start.sh"]
