"""Audit orchestrator — entry point for processing submitted URLs."""
import json

import aiosqlite
from loguru import logger

from .base_agent import detect_platform
from .website_agent import audit_website
from .amazon_agent import audit_amazon
from ...repositories.audit_repository import AuditRepository
from ...repositories.finding_repository import FindingRepository
from ...repositories.company_repository import CompanyRepository


async def run_audit(audit_id: int, db: aiosqlite.Connection) -> None:
    """Full audit flow: fetch URL, run agent, save results, update company."""
    audit_repo = AuditRepository(db)
    finding_repo = FindingRepository(db)
    company_repo = CompanyRepository(db)

    audit = await audit_repo.get_by_id(audit_id)
    if not audit:
        logger.error("Audit {} not found", audit_id)
        return

    url = audit["url"]
    platform = audit["platform"]
    logger.info("Processing audit {} — {} ({})", audit_id, url[:60], platform)

    # Set status to processing
    await db.execute("UPDATE audits SET status = 'processing' WHERE id = ?", (audit_id,))
    await db.commit()

    try:
        # Run appropriate agent
        if platform == "amazon_product":
            result = await audit_amazon(url)
        else:
            result = await audit_website(url)

        # Helper: serialize LocalizedText or plain str to JSON string
        def _loc(val) -> str:
            if hasattr(val, "model_dump"):
                return json.dumps(val.model_dump(), ensure_ascii=False)
            return str(val)

        # Save findings
        for f in result.findings:
            await finding_repo.create(
                audit_id=audit_id,
                type=f.type,
                severity=f.severity,
                title=_loc(f.title),
                description=_loc(f.description),
                evidence_url=f.evidence_url,
                confidence=f.confidence,
            )

        # Update audit with results
        await audit_repo.update_result(
            audit_id=audit_id,
            trust_score=result.trust_score,
            severity=result.severity,
            ai_summary=_loc(result.ai_summary),
            metadata=result.metadata or {},
            status="done",
        )

        # Update title/subtitle if agent provided better ones
        if result.title:
            await db.execute(
                "UPDATE audits SET title = ?, subtitle = ? WHERE id = ?",
                (_loc(result.title), _loc(result.subtitle), audit_id),
            )
            await db.commit()

        # Recalculate company score
        company_id = audit["company_id"]
        await _recalculate_company(db, company_id)

        logger.info("Audit {} done — score={}, {} findings", audit_id, result.trust_score, len(result.findings))

    except TimeoutError as e:
        logger.error("Audit {} timed out: {}", audit_id, e)
        await audit_repo.update_failure(audit_id, "Audit failed: analysis timeout")

    except ConnectionError as e:
        logger.error("Audit {} connection error: {}", audit_id, e)
        await audit_repo.update_failure(audit_id, "Audit failed: unable to access URL")

    except Exception as e:
        logger.error("Audit {} failed: {}", audit_id, e)
        await audit_repo.update_failure(audit_id, "Audit failed: unexpected error during analysis")


async def _recalculate_company(db: aiosqlite.Connection, company_id: int) -> None:
    """Recalculate company trust score from completed audits."""
    company_repo = CompanyRepository(db)

    cur = await db.execute(
        "SELECT trust_score FROM audits WHERE company_id = ? AND status = 'done' "
        "ORDER BY created_at DESC LIMIT 50",
        (company_id,),
    )
    rows = await cur.fetchall()

    if not rows:
        return

    # Weighted average: recent audits weigh more
    total_weight = 0
    weighted_sum = 0
    for i, row in enumerate(rows):
        weight = 1.0 / (1 + i * 0.1)  # newer audits have higher weight
        weighted_sum += row["trust_score"] * weight
        total_weight += weight

    score = round(weighted_sum / total_weight, 1) if total_weight else 50.0
    score = max(0.0, min(100.0, score))

    await company_repo.update_trust_score(company_id, score)

    # Update stats
    cur = await db.execute(
        "SELECT COUNT(*) FROM audits WHERE company_id = ? AND status = 'done'",
        (company_id,),
    )
    total = (await cur.fetchone())[0]

    # Top findings aggregation
    cur = await db.execute(
        "SELECT f.type, COUNT(*) as cnt FROM findings f "
        "JOIN audits a ON a.id = f.audit_id "
        "WHERE a.company_id = ? AND a.status = 'done' "
        "GROUP BY f.type ORDER BY cnt DESC LIMIT 5",
        (company_id,),
    )
    top = [row["type"] for row in await cur.fetchall()]

    await db.execute(
        "UPDATE companies SET total_audits = ?, top_findings = ?, updated_at = datetime('now') WHERE id = ?",
        (total, json.dumps(top), company_id),
    )
    await db.commit()
