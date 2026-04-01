"""Company service — leaderboard, company detail, trust score recalculation."""
import json
from typing import Optional

import aiosqlite
from loguru import logger

from ..repositories.audit_repository import AuditRepository
from ..repositories.company_repository import CompanyRepository
from ..schemas.audit import AuditCard
from ..schemas.company import CompanyDetail, CompanyResponse


def _row_to_company(row: aiosqlite.Row) -> CompanyResponse:
    """Convert a company DB row to CompanyResponse schema."""
    top_findings_raw = row["top_findings"]
    if isinstance(top_findings_raw, str):
        try:
            top_findings = json.loads(top_findings_raw)
        except (json.JSONDecodeError, TypeError):
            top_findings = []
    else:
        top_findings = top_findings_raw or []

    return CompanyResponse(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        domain=row["domain"],
        category=row["category"],
        description=row["description"],
        logo_url=row["logo_url"],
        trust_score=row["trust_score"],
        total_audits=row["total_audits"],
        trend_30d=row["trend_30d"],
        top_findings=top_findings,
    )


def _audit_row_to_card(row: aiosqlite.Row) -> AuditCard:
    """Convert a joined audit row to AuditCard."""
    return AuditCard(
        id=row["id"],
        company_id=row["company_id"],
        company_name=row["company_name"],
        company_slug=row["company_slug"],
        company_logo=row["company_logo"],
        url=row["url"],
        platform=row["platform"],
        title=row["title"],
        subtitle=row["subtitle"],
        trust_score=row["trust_score"],
        severity=row["severity"],
        ai_summary=row["ai_summary"],
        findings_count=row["findings_count"] if "findings_count" in row.keys() else 0,
        status=row["status"],
        views=row["views"],
        created_at=row["created_at"],
    )


class CompanyService:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.companies = CompanyRepository(db)
        self.audits = AuditRepository(db)

    async def get_company(self, slug: str) -> Optional[CompanyDetail]:
        """Get company with recent audits."""
        row = await self.companies.get_by_slug(slug)
        if not row:
            return None

        company = _row_to_company(row)

        # Recent audits (last 10)
        audit_rows, _ = await self.audits.get_by_company(
            company_id=row["id"], page=1, per_page=10
        )
        recent_audits = [_audit_row_to_card(a) for a in audit_rows]

        return CompanyDetail(
            **company.model_dump(),
            recent_audits=recent_audits,
        )

    async def get_company_audits(
        self, slug: str, page: int = 1, per_page: int = 20
    ) -> Optional[dict]:
        """Get paginated audits for a company by slug."""
        row = await self.companies.get_by_slug(slug)
        if not row:
            return None

        page = max(1, page)
        per_page = max(1, min(100, per_page))

        audit_rows, total = await self.audits.get_by_company(
            company_id=row["id"], page=page, per_page=per_page
        )
        items = [_audit_row_to_card(a) for a in audit_rows]
        has_more = (page * per_page) < total

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": has_more,
        }

    async def get_leaderboard(
        self, order: str = "worst", limit: int = 20
    ) -> list[CompanyResponse]:
        """Get companies sorted by trust score."""
        limit = max(1, min(100, limit))
        rows = await self.companies.get_all(order_by=order, limit=limit)
        return [_row_to_company(r) for r in rows]

    async def recalculate_score(self, company_id: int) -> float:
        """
        Recalculate company trust score as weighted average of audit scores.
        Recent audits have more weight.
        """
        cur = await self.db.execute(
            "SELECT trust_score, created_at FROM audits "
            "WHERE company_id = ? AND status = 'done' "
            "ORDER BY created_at DESC LIMIT 50",
            (company_id,),
        )
        rows = await cur.fetchall()

        if not rows:
            return 50.0

        # Weighted average: newer audits count more
        total_weight = 0.0
        weighted_sum = 0.0
        for i, row in enumerate(rows):
            weight = 1.0 / (1.0 + i * 0.3)  # Decay factor
            weighted_sum += row["trust_score"] * weight
            total_weight += weight

        score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 50.0
        score = max(0.0, min(100.0, score))

        await self.companies.update_trust_score(company_id, score)
        await self.companies.update_stats(company_id)

        logger.info("Recalculated trust score for company_id={}: {}", company_id, score)
        return score

    async def get_stats(self) -> dict:
        """Public stats: total audits, companies, findings, audits today."""
        cur = await self.db.execute(
            "SELECT COUNT(*) FROM audits WHERE status = 'done'"
        )
        total_audits = (await cur.fetchone())[0]

        cur = await self.db.execute("SELECT COUNT(*) FROM companies")
        total_companies = (await cur.fetchone())[0]

        cur = await self.db.execute("SELECT COUNT(*) FROM findings")
        total_findings = (await cur.fetchone())[0]

        cur = await self.db.execute(
            "SELECT COUNT(*) FROM audits "
            "WHERE status = 'done' AND created_at >= datetime('now', '-1 day')"
        )
        audits_today = (await cur.fetchone())[0]

        return {
            "total_audits": total_audits,
            "total_companies": total_companies,
            "total_findings": total_findings,
            "audits_today": audits_today,
        }

    async def search(self, query: str) -> list[CompanyResponse]:
        """Search companies by name or domain."""
        if not query or len(query) < 2:
            return []
        rows = await self.companies.search(query)
        return [_row_to_company(r) for r in rows]
