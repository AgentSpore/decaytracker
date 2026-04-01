"""Audit request/response schemas — Pydantic v2."""
from pydantic import BaseModel, Field, field_validator


class AuditRequest(BaseModel):
    url: str = Field(..., min_length=5, max_length=2000)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class FindingResponse(BaseModel):
    id: int
    type: str
    severity: str
    title: str
    description: str
    evidence_url: str
    confidence: float


class AuditCard(BaseModel):
    id: int
    company_id: int
    company_name: str
    company_slug: str
    company_logo: str
    url: str
    platform: str
    title: str
    subtitle: str
    trust_score: int
    severity: str
    ai_summary: str
    findings_count: int
    status: str
    views: int
    created_at: str


class AuditDetail(AuditCard):
    findings: list[FindingResponse]
    metadata: dict
