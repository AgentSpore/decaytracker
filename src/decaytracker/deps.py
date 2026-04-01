"""
FastAPI dependency injection — service factories using Annotated + Depends.
"""
from typing import Annotated, AsyncGenerator

import aiosqlite
from fastapi import Depends

from .database import get_db
from .services.audit_service import AuditService
from .services.company_service import CompanyService

# Base DB dependency
DBDep = Annotated[aiosqlite.Connection, Depends(get_db)]


# Service factory dependencies
async def get_audit_service(db: DBDep) -> AuditService:
    return AuditService(db)


async def get_company_service(db: DBDep) -> CompanyService:
    return CompanyService(db)


# Annotated type aliases for clean router signatures
AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
