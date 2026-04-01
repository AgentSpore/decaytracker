"""
DecayTracker v2 — The Trust Feed.
AI-powered URL audits forming a public trust feed.
"""
import asyncio
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .database import init_db, DB_PATH
from .api.feed import router as feed_router
from .api.companies import router as companies_router


async def _resume_pending_audits():
    """Resume pending/processing audits that were interrupted by a restart."""
    await asyncio.sleep(5)  # wait for server to be fully ready
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            import json as _json

            # Reset processing → pending (they were mid-flight when server died)
            await db.execute("UPDATE audits SET status = 'pending' WHERE status = 'processing'")
            await db.commit()

            # Clean up broken JSON titles/summaries from old LocalizedText schema
            cur = await db.execute("SELECT id, title, subtitle, ai_summary FROM audits WHERE title LIKE '{%' OR ai_summary LIKE '{%'")
            broken = await cur.fetchall()
            for row in broken:
                updates = {}
                for field in ("title", "subtitle", "ai_summary"):
                    val = row[field]
                    if val and val.startswith("{"):
                        try:
                            parsed = _json.loads(val)
                            updates[field] = parsed.get("en", val)
                        except _json.JSONDecodeError:
                            pass
                if updates:
                    sets = ", ".join(f"{k} = ?" for k in updates)
                    vals = list(updates.values()) + [row["id"]]
                    await db.execute(f"UPDATE audits SET {sets} WHERE id = ?", vals)
            if broken:
                await db.commit()
                logger.info("Cleaned {} audits with broken JSON fields", len(broken))

            cur = await db.execute(
                "SELECT id FROM audits WHERE status = 'pending' ORDER BY created_at ASC LIMIT 20"
            )
            pending = await cur.fetchall()

        if not pending:
            logger.info("No pending audits to resume")
            return

        logger.info("Resuming {} pending audits...", len(pending))
        from .services.audit_agent import run_audit_agent
        for row in pending:
            asyncio.create_task(run_audit_agent(row["id"]))
            await asyncio.sleep(2)  # stagger to avoid overwhelming

    except Exception as e:
        logger.error("Failed to resume pending audits: {}", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready")
    # Resume interrupted audits in background
    asyncio.create_task(_resume_pending_audits())
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="DecayTracker",
    description="The Trust Feed — AI-powered URL audits for corporate trust scoring",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feed_router)
app.include_router(companies_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "decaytracker", "version": "2.0.0"}
