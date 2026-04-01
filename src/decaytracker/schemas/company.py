"""Company response schemas — Pydantic v2."""
from __future__ import annotations

from pydantic import BaseModel

from .audit import AuditCard


class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    domain: str
    category: str
    description: str
    logo_url: str
    trust_score: float
    total_audits: int
    trend_30d: float
    top_findings: list[str]


class CompanyDetail(CompanyResponse):
    recent_audits: list[AuditCard]
