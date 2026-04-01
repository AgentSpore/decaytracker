"""Company repository — all DB operations for companies table."""
import json
import re
from typing import Optional

import aiosqlite


def _slugify(name: str) -> str:
    """Generate URL-safe slug from company name."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug


class CompanyRepository:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def get_or_create_by_domain(self, domain: str, name: str) -> aiosqlite.Row:
        """Find company by domain or create a new one. Returns the row."""
        cur = await self.db.execute(
            "SELECT * FROM companies WHERE domain = ?", (domain,)
        )
        row = await cur.fetchone()
        if row:
            return row

        slug = _slugify(name)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while True:
            check = await self.db.execute(
                "SELECT 1 FROM companies WHERE slug = ?", (slug,)
            )
            if await check.fetchone() is None:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        await self.db.execute(
            "INSERT INTO companies (name, slug, domain, logo_url) VALUES (?, ?, ?, ?)",
            (name, slug, domain, logo_url),
        )
        await self.db.commit()

        cur = await self.db.execute(
            "SELECT * FROM companies WHERE domain = ?", (domain,)
        )
        return await cur.fetchone()

    async def get_by_slug(self, slug: str) -> Optional[aiosqlite.Row]:
        cur = await self.db.execute(
            "SELECT * FROM companies WHERE slug = ?", (slug,)
        )
        return await cur.fetchone()

    async def get_by_id(self, company_id: int) -> Optional[aiosqlite.Row]:
        cur = await self.db.execute(
            "SELECT * FROM companies WHERE id = ?", (company_id,)
        )
        return await cur.fetchone()

    async def get_all(
        self,
        order_by: str = "trust_score ASC",
        limit: int = 20,
        offset: int = 0,
    ) -> list[aiosqlite.Row]:
        """Get companies for leaderboard. order_by is sanitized in the service layer."""
        allowed_orders = {
            "best": "trust_score DESC",
            "worst": "trust_score ASC",
            "most_audited": "total_audits DESC",
        }
        sql_order = allowed_orders.get(order_by, "trust_score ASC")
        cur = await self.db.execute(
            f"SELECT * FROM companies ORDER BY {sql_order} LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return await cur.fetchall()

    async def update_trust_score(self, company_id: int, score: float) -> None:
        await self.db.execute(
            "UPDATE companies SET trust_score = ?, updated_at = datetime('now') WHERE id = ?",
            (round(score, 1), company_id),
        )
        await self.db.commit()

    async def update_stats(self, company_id: int) -> None:
        """Recalculate total_audits, trend_30d, top_findings from audits/findings."""
        # Total audits (only done)
        cur = await self.db.execute(
            "SELECT COUNT(*) FROM audits WHERE company_id = ? AND status = 'done'",
            (company_id,),
        )
        total = (await cur.fetchone())[0]

        # Average trust_score from last 30 days vs previous 30 days for trend
        cur = await self.db.execute(
            "SELECT AVG(trust_score) FROM audits "
            "WHERE company_id = ? AND status = 'done' "
            "AND created_at >= datetime('now', '-30 days')",
            (company_id,),
        )
        avg_recent = (await cur.fetchone())[0] or 50.0

        cur = await self.db.execute(
            "SELECT AVG(trust_score) FROM audits "
            "WHERE company_id = ? AND status = 'done' "
            "AND created_at >= datetime('now', '-60 days') "
            "AND created_at < datetime('now', '-30 days')",
            (company_id,),
        )
        avg_prev = (await cur.fetchone())[0] or avg_recent
        trend = round(avg_recent - avg_prev, 1)

        # Top finding types (most frequent)
        cur = await self.db.execute(
            "SELECT f.type, COUNT(*) as cnt "
            "FROM findings f "
            "JOIN audits a ON a.id = f.audit_id "
            "WHERE a.company_id = ? AND a.status = 'done' "
            "GROUP BY f.type ORDER BY cnt DESC LIMIT 5",
            (company_id,),
        )
        rows = await cur.fetchall()
        top_findings = [r["type"] for r in rows]

        await self.db.execute(
            "UPDATE companies SET total_audits = ?, trend_30d = ?, top_findings = ?, "
            "updated_at = datetime('now') WHERE id = ?",
            (total, trend, json.dumps(top_findings), company_id),
        )
        await self.db.commit()

    async def search(self, query: str) -> list[aiosqlite.Row]:
        """Search companies by name (case-insensitive LIKE)."""
        pattern = f"%{query}%"
        cur = await self.db.execute(
            "SELECT * FROM companies WHERE name LIKE ? OR domain LIKE ? "
            "ORDER BY total_audits DESC LIMIT 20",
            (pattern, pattern),
        )
        return await cur.fetchall()
