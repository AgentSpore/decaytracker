# DecayTracker — Architecture Deep Dive

## Overview
The Enshittification Index — crowdsourced product decay tracker with AI-verified votes and auto-research agent.

## Architecture

### Backend (FastAPI + SQLite)
Layered architecture: Router → Service → Repository → Schema

```
src/decaytracker/
  api/            # Thin HTTP routers (products.py, research.py)
  services/       # Business logic (product_service, vote_service, moderator, researcher)
  repositories/   # Data access layer (product_repo, vote_repo, event_repo)
  schemas/        # Pydantic models (product, vote, event)
  deps.py         # FastAPI Depends injection
  database.py     # SQLite init, migrations, seed data
  main.py         # App entrypoint, CORS, lifespan
```

### Frontend (Next.js 16 + React 19)
- Design: Editorial Mono B (Playfair Display 900, Source Sans 3, black/white + red)
- State: Zustand store with API client
- i18n: EN/RU/CN via localStorage locale
- Charts: Recharts AreaChart (red gradient)

### Key Decisions

**SQLite over Postgres**: Single-file DB, zero-config, WAL mode for concurrent reads. Perfect for <10K products. Migration path: aiosqlite → asyncpg when needed.

**pydantic-ai with FallbackModel**: Free LLM via OpenRouter (nemotron → minimax → stepfun). Structured output ensures consistent moderation results.

**Playwright for Google Search**: Persistent Chrome profile avoids CAPTCHA. Custom web_search() extracts titles+snippets only (~500 chars vs 50K accessibility tree from MCP).

**Background vote moderation**: Vote saved as pending → BackgroundTask triggers AI agent → searches Google → approve/reject/adjust → score recalculated. Non-blocking for user.

**Research Agent**: 3 queries per product (price increase, enshittification, alternatives). Deduplicates against existing events. Runs on cron or manual trigger.

**Google Favicons API**: `google.com/s2/favicons?domain={domain}&sz=64` — 100% uptime vs Clearbit (DNS issues) or logo.dev (token required).

## Edge Cases
- Rate limit: 3 votes per session per product per 24h
- Products submitted via Request form get `status: pending` (not shown in list)
- Category filter uses AND (not WHERE override) — fixed SQL bug
- `/products/search` route placed BEFORE `/{slug}` to avoid "search" matching as slug
- Research agent skips products with no domain
- Auto-approve low-impact votes (|impact| <= 3, no comment) — fast path

## Data Flow
1. User votes → saved as pending → background AI moderation
2. Moderator searches Google → fact-checks claim → approve/reject/adjust
3. Score recalculated: base_score + impact adjustments (clamped 0-100)
4. Research agent discovers new events → saved to DB → score recalculated
