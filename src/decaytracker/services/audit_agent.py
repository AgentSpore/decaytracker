"""Audit agent — bridges background task with AI orchestrator."""
import asyncio

import aiosqlite
from loguru import logger

from ..database import DB_PATH

# Task 5: Limit concurrent Playwright instances to avoid resource exhaustion
_AUDIT_SEMAPHORE = asyncio.Semaphore(2)


async def run_audit_agent(audit_id: int) -> None:
    """Run the AI audit agent for a given audit_id.

    Opens its own DB connection since BackgroundTasks run after response.
    Concurrency limited to 2 simultaneous audits via semaphore.
    """
    logger.info("Starting audit agent for audit_id={} (acquiring semaphore)", audit_id)

    async with _AUDIT_SEMAPHORE:
        logger.info("Semaphore acquired for audit_id={}", audit_id)
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute("PRAGMA foreign_keys=ON")

                from .agents.audit_orchestrator import run_audit
                await run_audit(audit_id, db)
        except Exception as e:
            logger.error("Audit agent failed for audit_id={}: {}", audit_id, e)
            # Try to mark as failed
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("UPDATE audits SET status = 'failed' WHERE id = ?", (audit_id,))
                    await db.commit()
            except Exception:
                pass
