# DecayTracker — The Enshittification Index

> Crowdsourced product decay tracker with AI-verified votes and auto-research agent.

![Editorial Mono B](https://img.shields.io/badge/design-Editorial%20Mono-black) ![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![Next.js 16](https://img.shields.io/badge/next.js-16-black) ![License](https://img.shields.io/badge/license-MIT-green)

## What is this?

DecayTracker tracks how products get worse over time — price increases, feature removals, added ads, privacy erosion. Users vote on decay events, and an AI agent fact-checks every claim using Google search.

## UI Walkthrough

### Homepage — The Index
- Black masthead with Playfair Display "The Index"
- Search, category filter (13 categories), sort (Score/Votes/Name)
- 20 tracked products with Google Favicon logos and decay scores (0-100)
- Language switcher: English / Русский / 中文
- "+ Request" button for product submissions (reviewed before appearing)

### Product Detail
- Company logo, description, current price, decay score badge
- Key Metrics: Events, Votes, Alternatives count
- Alternatives list (seed + auto-discovered by research agent)
- Decay Timeline chart (Recharts AreaChart, red gradient)
- Events timeline with impact scores, dates, source links
- Community Votes with AI analysis (confidence %, fact-check sources as green pills)

### Vote Dialog
- Dimension: Pricing / Features / Ads / Privacy / Support / Performance / UX
- Impact slider: -10 (Catastrophic) to +10 (Improvement)
- Comment field (AI fact-checked via Google search)
- Real-time polling for moderation result

## Architecture

```
Backend:  FastAPI + aiosqlite (Router → Service → Repository → Schema)
Frontend: Next.js 16 + React 19 + Zustand + Recharts + Tailwind v4
AI:       pydantic-ai + FallbackModel (OpenRouter free tier) + Playwright
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/products | List active products (filter: category, search) |
| GET | /api/products/{slug} | Product detail with events, votes, alternatives |
| GET | /api/products/search?q= | Search products |
| POST | /api/products | Request new product (pending review) |
| POST | /api/products/{slug}/vote | Submit vote (AI-moderated in background) |
| GET | /api/votes/{id} | Poll vote moderation status |
| GET | /api/categories | List categories |
| POST | /api/research | Trigger research on all products |
| POST | /api/research/{slug} | Research single product |

## Quick Start

```bash
# Backend
cd services/decaytracker
uv sync
make dev        # http://localhost:8790

# Frontend
cd frontend
npm install
npm run dev     # http://localhost:3001

# Tests
make test       # 35 e2e tests
make smoke      # Quick health check
```

## Market Analysis

### Problem
Users have no centralized, data-driven way to track how products degrade over time. Complaints are scattered across Reddit, Twitter, forums.

### TAM / SAM / SOM
- **TAM**: $2.1B — consumer review & advocacy market
- **SAM**: $420M — tech product tracking + comparison tools
- **SOM**: $8.4M — early adopters who actively track enshittification

### ICP (Ideal Customer Profile)
- Tech-savvy consumers (25-45) frustrated with product decay
- Journalists covering tech industry trends
- Advocacy groups monitoring corporate behavior
- Developers evaluating tool alternatives

### Economics
| Metric | Value |
|--------|-------|
| Freemium model | Free access, Pro $9.99/mo (API, alerts, reports) |
| Gross margin | 94% (SQLite + free LLM tier) |
| CAC | ~$5 (organic via Reddit, HN, Twitter) |
| LTV | $120 (12-month avg retention) |
| LTV/CAC | 24x |

### Risks
1. **Legal**: Companies may dispute decay ratings → mitigation: AI fact-checking + source citations
2. **Gaming**: Coordinated voting → mitigation: rate limits + AI moderation
3. **Scale**: SQLite single-file → migration path to Postgres when >10K products
4. **LLM costs**: Using free tier → switch to paid models only for complex cases

## Idea Scoring

| Criteria | Score |
|----------|-------|
| Uniqueness | 9/10 — no dedicated enshittification tracker exists |
| Pain level | 8/10 — universal frustration, high emotional engagement |
| Monetization | 7/10 — Pro tier, API access, corporate reputation monitoring |
| Virality | 9/10 — shareable scores, "X got worse" tweets, Reddit discussions |
| Feasibility | 8/10 — MVP built in 1 day with AI automation |
| **Total** | **41/50** |

## License
MIT
