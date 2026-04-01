"""Audit repository — all DB operations for audits table."""
import json
from typing import Optional

import aiosqlite


class AuditRepository:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(
        self,
        company_id: int,
        url: str,
        platform: str,
        title: str,
        subtitle: str = "",
    ) -> int:
        """Insert a new audit in 'pending' status. Returns audit_id."""
        cur = await self.db.execute(
            "INSERT INTO audits (company_id, url, platform, title, subtitle) "
            "VALUES (?, ?, ?, ?, ?)",
            (company_id, url, platform, title, subtitle),
        )
        await self.db.commit()
        return cur.lastrowid

    async def get_by_id(self, audit_id: int) -> Optional[aiosqlite.Row]:
        """Get audit with company info via JOIN."""
        cur = await self.db.execute(
            "SELECT a.*, "
            "c.name AS company_name, c.slug AS company_slug, c.logo_url AS company_logo "
            "FROM audits a "
            "JOIN companies c ON c.id = a.company_id "
            "WHERE a.id = ?",
            (audit_id,),
        )
        return await cur.fetchone()

    async def get_feed(
        self,
        page: int = 1,
        per_page: int = 20,
        platform_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
    ) -> tuple[list[aiosqlite.Row], int]:
        """Paginated feed of audits. Returns (rows, total_count)."""
        where_clauses = ["a.status IN ('done', 'pending', 'processing', 'failed')"]
        params: list = []

        if platform_filter:
            where_clauses.append("a.platform = ?")
            params.append(platform_filter)
        if severity_filter:
            where_clauses.append("a.severity = ?")
            params.append(severity_filter)

        where_sql = " AND ".join(where_clauses)

        # Total count
        cur = await self.db.execute(
            f"SELECT COUNT(*) FROM audits a WHERE {where_sql}", params
        )
        total = (await cur.fetchone())[0]

        # Paginated results
        offset = (page - 1) * per_page
        cur = await self.db.execute(
            f"SELECT a.*, "
            f"c.name AS company_name, c.slug AS company_slug, c.logo_url AS company_logo, "
            f"(SELECT COUNT(*) FROM findings f WHERE f.audit_id = a.id) AS findings_count "
            f"FROM audits a "
            f"JOIN companies c ON c.id = a.company_id "
            f"WHERE {where_sql} "
            f"ORDER BY a.created_at DESC "
            f"LIMIT ? OFFSET ?",
            [*params, per_page, offset],
        )
        rows = await cur.fetchall()
        return rows, total

    async def get_by_company(
        self,
        company_id: int,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[aiosqlite.Row], int]:
        """Paginated audits for a company."""
        cur = await self.db.execute(
            "SELECT COUNT(*) FROM audits WHERE company_id = ? AND status = 'done'",
            (company_id,),
        )
        total = (await cur.fetchone())[0]

        offset = (page - 1) * per_page
        cur = await self.db.execute(
            "SELECT a.*, "
            "c.name AS company_name, c.slug AS company_slug, c.logo_url AS company_logo, "
            "(SELECT COUNT(*) FROM findings f WHERE f.audit_id = a.id) AS findings_count "
            "FROM audits a "
            "JOIN companies c ON c.id = a.company_id "
            "WHERE a.company_id = ? AND a.status = 'done' "
            "ORDER BY a.created_at DESC "
            "LIMIT ? OFFSET ?",
            (company_id, per_page, offset),
        )
        rows = await cur.fetchall()
        return rows, total

    async def update_result(
        self,
        audit_id: int,
        trust_score: int,
        severity: str,
        ai_summary: str,
        metadata: dict,
        status: str,
    ) -> None:
        """Update audit with AI analysis results."""
        await self.db.execute(
            "UPDATE audits SET trust_score = ?, severity = ?, ai_summary = ?, "
            "metadata = ?, status = ? WHERE id = ?",
            (trust_score, severity, ai_summary, json.dumps(metadata), status, audit_id),
        )
        await self.db.commit()

    async def update_failure(self, audit_id: int, reason: str) -> None:
        """Set audit status to 'failed' and store reason in ai_summary."""
        await self.db.execute(
            "UPDATE audits SET status = 'failed', ai_summary = ? WHERE id = ?",
            (reason, audit_id),
        )
        await self.db.commit()

    async def reset_for_retry(self, audit_id: int) -> None:
        """Reset a failed audit to 'pending' for retry."""
        await self.db.execute(
            "UPDATE audits SET status = 'pending', ai_summary = '' WHERE id = ?",
            (audit_id,),
        )
        await self.db.commit()

    async def get_recent_by_url(self, url: str, hours: int = 24) -> Optional[aiosqlite.Row]:
        """Find a recent audit for this exact URL within the last N hours.

        Prioritizes: done > processing > pending. Returns the most recent match.
        """
        cur = await self.db.execute(
            "SELECT a.*, "
            "c.name AS company_name, c.slug AS company_slug, c.logo_url AS company_logo "
            "FROM audits a "
            "JOIN companies c ON c.id = a.company_id "
            "WHERE a.url = ? "
            "AND a.created_at >= datetime('now', ? || ' hours') "
            "ORDER BY "
            "  CASE a.status "
            "    WHEN 'done' THEN 0 "
            "    WHEN 'processing' THEN 1 "
            "    WHEN 'pending' THEN 2 "
            "    ELSE 3 "
            "  END, "
            "  a.created_at DESC "
            "LIMIT 1",
            (url, f"-{hours}"),
        )
        return await cur.fetchone()

    async def increment_views(self, audit_id: int) -> None:
        await self.db.execute(
            "UPDATE audits SET views = views + 1 WHERE id = ?", (audit_id,)
        )
        await self.db.commit()
