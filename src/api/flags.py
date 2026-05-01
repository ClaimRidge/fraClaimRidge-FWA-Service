from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from src.repositories.flag_repo import FlagRepository
from src.models.database import FraudFlag, Severity
from src.schemas.flag import FlagResponse
from src.dependencies import get_flag_repo, get_current_tenant
import uuid

router = APIRouter(prefix="/v1/fwa/flags", tags=["Flags"])

@router.get("/", response_model=List[FlagResponse])
async def list_flags(
    layer: Optional[str] = None,
    severity: Optional[Severity] = None,
    tenant_id: str = Depends(get_current_tenant),
    repo: FlagRepository = Depends(get_flag_repo)
):
    flags = await repo.list(tenant_id)
    if layer:
        flags = [f for f in flags if f.layer == layer]
    if severity:
        flags = [f for f in flags if f.severity == severity]
    return flags

@router.get("/{flag_id}", response_model=FlagResponse)
async def get_flag(
    flag_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant),
    repo: FlagRepository = Depends(get_flag_repo)
):
    flag = await repo.get_by_id(flag_id, tenant_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag
