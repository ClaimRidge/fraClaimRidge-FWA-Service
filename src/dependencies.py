from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db_session
from src.repositories.flag_repo import FlagRepository, CaseRepository
from src.repositories.base import BaseRepository
from src.models.database import FraudScore
from typing import Optional

async def get_current_tenant(x_tenant_id: str = Header(..., alias="X-Tenant-ID")) -> str:
    """
    Extracts the tenant_id from the custom header. 
    In production, this would be validated against a JWT token.
    """
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Tenant ID header missing")
    return x_tenant_id

async def get_case_repo(session: AsyncSession = Depends(get_db_session)) -> CaseRepository:
    """
    Dependency provider for CaseRepository.
    """
    return CaseRepository(session)

async def get_flag_repo(session: AsyncSession = Depends(get_db_session)) -> FlagRepository:
    """
    Dependency provider for FlagRepository.
    """
    return FlagRepository(session)

async def get_score_repo(session: AsyncSession = Depends(get_db_session)) -> BaseRepository[FraudScore]:
    """
    Dependency provider for FraudScore repository.
    """
    return BaseRepository(FraudScore, session)
