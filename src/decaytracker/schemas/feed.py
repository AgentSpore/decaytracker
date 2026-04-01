"""Feed pagination schema — Pydantic v2."""
from pydantic import BaseModel

from .audit import AuditCard


class FeedResponse(BaseModel):
    items: list[AuditCard]
    total: int
    page: int
    per_page: int
    has_more: bool
