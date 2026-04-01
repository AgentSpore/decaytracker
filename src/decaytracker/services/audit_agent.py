"""Audit agent — bridges background task with AI orchestrator."""
import asyncio

import aiosqlite
from loguru import logger

from ..database import DB_PATH

# Limit concurrent Playwright instances to avoid OOM
_AUDIT_SEMAPHORE = asyncio.Semaphore(1)

# Queue to prevent unbounded task accumulation
_MAX_QUEUED = 10
_queue_size = 0
_queue_lock = asyncio.Lock()


async def run_audit_agent(audit_id: int) -> None:
    """Run the AI audit agent for a given audit_id.

    Concurrency limited to 1 simultaneous audit (Playwright is heavy).
    Queue limited to 10 pending tasks to prevent OOM.
    """
    global _queue_size

    async with _queue_lock:
        if _queue_size >= _MAX_QUEUED:
            logger.warning("Audit queue full ({}/{}), skipping audit_id={}", _queue_size, _MAX_QUEUED, audit_id)
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute(
                        "UPDATE audits SET status = 'pending', ai_summary = 'Server busy, will retry later' WHERE id = ?",
                        (audit_id,),
                    )
                    await db.commit()
            except Exception:
                pass
            return
        _queue_size += 1

    logger.info("Audit agent queued audit_id={} (queue {}/{})", audit_id, _queue_size, _MAX_QUEUED)

    try:
        async with _AUDIT_SEMAPHORE:
            logger.info("Semaphore acquired for audit_id={}", audit_id)
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
    finally:
        async with _queue_lock:
            _queue_size = max(0, _queue_size - 1)
