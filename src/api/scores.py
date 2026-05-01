from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.repositories.base import BaseRepository
from src.models.database import FraudScore
from src.schemas.score import ScoreResponse
from src.dependencies import get_score_repo, get_current_tenant
from sqlalchemy import select

router = APIRouter(prefix="/v1/fwa/scores", tags=["Scores"])

@router.get("/claim/{claim_id}", response_model=List[ScoreResponse])
async def get_claim_scores(
    claim_id: str,
    tenant_id: str = Depends(get_current_tenant),
    repo: BaseRepository[FraudScore] = Depends(get_score_repo)
):
    # Specialized query for claim_id
    query = select(repo.model).where(
        repo.model.claim_id == claim_id, 
        repo.model.tenant_id == tenant_id
    )
    result = await repo.session.execute(query)
    scores = result.scalars().all()
    
    if not scores:
        raise HTTPException(status_code=404, detail="No scores found for this claim")
        
    return list(scores)
