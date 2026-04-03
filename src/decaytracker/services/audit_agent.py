"""Audit agent — processes audits one at a time with auto-pickup."""
import asyncio

import aiosqlite
from loguru import logger

from ..database import DB_PATH

# Only 1 Playwright at a time
_AUDIT_SEMAPHORE = asyncio.Semaphore(1)
# Track in-flight audit to prevent re-pickup
_current_audit_id: int | None = None


async def run_audit_agent(audit_id: int) -> None:
    """Run audit, then auto-pickup next pending audit from DB."""
    global _current_audit_id

    # Prevent re-processing same audit
    if _current_audit_id == audit_id:
        logger.warning("Audit {} already in-flight, skipping", audit_id)
        return

    async with _AUDIT_SEMAPHORE:
        _current_audit_id = audit_id
        await _process_one(audit_id)
        _current_audit_id = None

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

            # CRITICAL: set processing BEFORE running audit to prevent re-pickup
            await db.execute("UPDATE audits SET status = 'processing' WHERE id = ? AND status = 'pending'", (audit_id,))
            await db.commit()

            # Check it was actually pending (not already done/failed)
            cur = await db.execute("SELECT status FROM audits WHERE id = ?", (audit_id,))
            row = await cur.fetchone()
            if not row or row["status"] not in ("processing",):
                logger.info("Audit {} status is '{}', skipping", audit_id, row["status"] if row else "not found")
                return

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
    await asyncio.sleep(2)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            # ONLY pending — never pick up done/failed/processing
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
