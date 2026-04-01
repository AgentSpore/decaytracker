"""
Companies router — leaderboard, company detail, company audits.
All business logic lives in CompanyService (injected via Depends).
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..deps import CompanyServiceDep
from ..schemas.company import CompanyDetail, CompanyResponse

router = APIRouter(prefix="/api")


@router.get("/companies", response_model=list[CompanyResponse])
async def get_leaderboard(
    svc: CompanyServiceDep,
    order: str = Query("worst", pattern="^(best|worst|most_audited)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """Get company leaderboard sorted by trust score or audit count."""
    return await svc.get_leaderboard(order=order, limit=limit)


@router.get("/companies/search", response_model=list[CompanyResponse])
async def search_companies(
    svc: CompanyServiceDep,
    q: str = Query(..., min_length=2, max_length=100),
):
    """Search companies by name or domain."""
    return await svc.search(q)


@router.get("/company/{slug}", response_model=CompanyDetail)
async def get_company(slug: str, svc: CompanyServiceDep):
    """Get company profile with recent audits."""
    result = await svc.get_company(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Company not found")
    return result


@router.get("/stats")
async def get_stats(svc: CompanyServiceDep):
    """Public stats: total audits, companies, findings."""
    return await svc.get_stats()


@router.get("/company/{slug}/audits")
async def get_company_audits(
    slug: str,
    svc: CompanyServiceDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Get paginated audits for a company."""
    result = await svc.get_company_audits(slug, page=page, per_page=per_page)
    if result is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return result
