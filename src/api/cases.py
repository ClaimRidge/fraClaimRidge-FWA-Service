from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.repositories.flag_repo import CaseRepository
from src.models.database import FraudCase, CaseStatus, Severity
from src.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from src.dependencies import get_case_repo, get_current_tenant
import uuid

router = APIRouter(prefix="/v1/fwa/cases", tags=["Cases"])

@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    status: Optional[CaseStatus] = None,
    severity: Optional[Severity] = None,
    tenant_id: str = Depends(get_current_tenant),
    repo: CaseRepository = Depends(get_case_repo)
):
    # Logic to filter and list cases
    cases = await repo.list(tenant_id)
    if status:
        cases = [c for c in cases if c.status == status]
    if severity:
        cases = [c for c in cases if c.severity == severity]
    return cases

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant),
    repo: CaseRepository = Depends(get_case_repo)
):
    case = await repo.get_with_flags(case_id, tenant_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: uuid.UUID,
    update_data: CaseUpdate,
    tenant_id: str = Depends(get_current_tenant),
    repo: CaseRepository = Depends(get_case_repo)
):
    case = await repo.update(case_id, tenant_id, **update_data.model_dump(exclude_unset=True))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
