from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from src.models.database import Severity
import uuid

class FlagBase(BaseModel):
    layer: str
    severity: Severity
    confidence: float
    entity_type: str
    entity_id: str
    description: str
    evidence: Dict[str, Any] = {}

class FlagResponse(FlagBase):
    id: uuid.UUID
    tenant_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
