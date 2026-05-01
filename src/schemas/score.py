from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ScoreBase(BaseModel):
    claim_id: str
    tenant_id: str
    l1_anomaly_score: Optional[float] = None
    l2_drift_score: Optional[float] = None
    l3_graph_score: Optional[float] = None
    l4_timeseries_score: Optional[float] = None
    composite_score: float
    confidence: float
    metadata_json: Dict[str, Any] = {}

class ScoreResponse(ScoreBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
