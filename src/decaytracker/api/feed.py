"""
Feed router — audit submission and public feed.
All business logic lives in AuditService (injected via Depends).
"""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from ..deps import AuditServiceDep
from ..schemas.audit import AuditDetail, AuditRequest
from ..schemas.feed import FeedResponse
from ..services.audit_agent import run_audit_agent
from ..services.url_validator import URLValidationError

router = APIRouter(prefix="/api")


@router.post("/audit", status_code=202)
async def submit_audit(
    body: AuditRequest,
    background_tasks: BackgroundTasks,
    svc: AuditServiceDep,
):
    """Submit a URL for AI audit. Returns immediately, audit runs in background."""
    try:
        result = await svc.submit_audit(body.url)
    except URLValidationError:
        raise HTTPException(status_code=422, detail="Invalid or disallowed URL")
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid URL")

    # Only schedule background audit for new (non-cached) submissions
    if not result.get("cached"):
        background_tasks.add_task(run_audit_agent, result["audit_id"])
    return result


@router.post("/audit/{audit_id}/retry", status_code=202)
async def retry_audit(
    audit_id: int,
    background_tasks: BackgroundTasks,
    svc: AuditServiceDep,
):
    """Retry a failed audit."""
    try:
        result = await svc.retry_audit(audit_id)
    except ValueError:
        raise HTTPException(status_code=409, detail="Only failed audits can be retried")

    if not result:
        raise HTTPException(status_code=404, detail="Audit not found")

    background_tasks.add_task(run_audit_agent, result["audit_id"])
    return result


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    svc: AuditServiceDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    platform: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    """Get the public trust feed — paginated list of completed audits."""
    return await svc.get_feed(
        page=page,
        per_page=per_page,
        platform=platform,
        severity=severity,
    )


@router.get("/audit/{audit_id}", response_model=AuditDetail)
async def get_audit(audit_id: int, svc: AuditServiceDep):
    """Get full audit details including findings."""
    result = await svc.get_audit(audit_id)
    if not result:
        raise HTTPException(status_code=404, detail="Audit not found")
    return result
