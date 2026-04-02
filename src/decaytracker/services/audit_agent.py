"""Audit agent — processes audits one at a time with auto-pickup."""
import asyncio

import aiosqlite
from loguru import logger

from ..database import DB_PATH

# Only 1 Playwright at a time
_AUDIT_SEMAPHORE = asyncio.Semaphore(1)


async def run_audit_agent(audit_id: int) -> None:
    """Run audit, then auto-pickup next pending audit from DB."""
    async with _AUDIT_SEMAPHORE:
        await _process_one(audit_id)

    # After finishing, check for more pending audits
    asyncio.create_task(_pickup_next())


async def _process_one(audit_id: int) -> None:
    """Process a single audit."""
    logger.info("Processing audit_id={}", audit_id)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA foreign_keys=ON")

            from .agents.audit_orchestrator import run_audit
            await run_audit(audit_id, db)
    except Exception as e:
        logger.error("Audit agent failed for audit_id={}: {}", audit_id, e)
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "UPDATE audits SET status = 'failed', ai_summary = 'Audit failed: server error' WHERE id = ?",
                    (audit_id,),
                )
                await db.commit()
        except Exception:
            pass


async def _pickup_next() -> None:
    """Find next pending audit in DB and process it."""
    await asyncio.sleep(1)  # small delay between audits
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT id FROM audits WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
            )
            row = await cur.fetchone()

        if row:
            logger.info("Auto-pickup: next pending audit_id={}", row["id"])
            await run_audit_agent(row["id"])
        else:
            logger.info("No more pending audits")
    except Exception as e:
        logger.error("Pickup failed: {}", e)
