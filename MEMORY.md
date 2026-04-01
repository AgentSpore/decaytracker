# DecayTracker — Change Log

## v0.1.0 (2026-03-27)
- Initial MVP: 20 seed products, 30 events, 16 alternatives
- AI vote moderation (pydantic-ai + Playwright Google search)
- Auto-Research Agent (3 queries/product, FallbackModel)
- Next.js 16 frontend: Editorial Mono B design
- i18n: EN/RU/CN with locale switcher
- Router-Service-Repository architecture
- 35 E2E tests (pytest + httpx), smoke test
- Dockerfile (multi-stage: Node + Python)
- Research cron via /api/research endpoint

## Research Agent Results (2026-03-27)
- Spotify: found 6 new events, 6 alternatives, updated price to $12.99/mo
- Discord: found 5 events (IPO, price increase, user exodus), 13 alternatives
- Netflix: found 3 events (casting removal, categories removal, March 2026 price hike), 10 alternatives
- GitHub: found 4 events, 3 alternatives
- Zoom: found 1 event, 3 alternatives
