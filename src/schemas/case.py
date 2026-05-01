from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from src.models.database import Severity, CaseStatus
import uuid

class CaseBase(BaseModel):
    title: str
    severity: Severity
    summary: Optional[str] = None
    metadata_json: Dict[str, Any] = {}

class CaseCreate(CaseBase):
    tenant_id: str

class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = None
    severity: Optional[Severity] = None
    investigator_id: Optional[str] = None
    summary: Optional[str] = None

class CaseResponse(CaseBase):
    id: uuid.UUID
    status: CaseStatus
    investigator_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
