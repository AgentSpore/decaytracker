"""Finding repository — all DB operations for findings table."""
import aiosqlite


class FindingRepository:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create(
        self,
        audit_id: int,
        type: str,
        severity: str,
        title: str,
        description: str = "",
        evidence_url: str = "",
        confidence: float = 0.5,
    ) -> int:
        cur = await self.db.execute(
            "INSERT INTO findings (audit_id, type, severity, title, description, evidence_url, confidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (audit_id, type, severity, title, description, evidence_url, confidence),
        )
        await self.db.commit()
        return cur.lastrowid

    async def create_many(self, audit_id: int, findings: list[dict]) -> int:
        """Bulk insert findings for an audit. Returns number of inserted rows."""
        if not findings:
            return 0

        for f in findings:
            await self.db.execute(
                "INSERT INTO findings (audit_id, type, severity, title, description, evidence_url, confidence) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    audit_id,
                    f.get("type", "enshittification"),
                    f.get("severity", "warning"),
                    f.get("title", ""),
                    f.get("description", ""),
                    f.get("evidence_url", ""),
                    f.get("confidence", 0.5),
                ),
            )
        await self.db.commit()
        return len(findings)

    async def get_by_audit(self, audit_id: int) -> list[aiosqlite.Row]:
        cur = await self.db.execute(
            "SELECT * FROM findings WHERE audit_id = ? ORDER BY confidence DESC",
            (audit_id,),
        )
        return await cur.fetchall()
