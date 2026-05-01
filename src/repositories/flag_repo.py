from src.repositories.base import BaseRepository
from src.models.database import FraudFlag, FraudCase, Severity, CaseStatus
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

class FlagRepository(BaseRepository[FraudFlag]):
    def __init__(self, session):
        super().__init__(FraudFlag, session)

    async def get_by_entity(self, entity_type: str, entity_id: str, tenant_id: str) -> List[FraudFlag]:
        query = select(self.model).where(
            and_(
                self.model.entity_type == entity_type,
                self.model.entity_id == entity_id,
                self.model.tenant_id == tenant_id
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

class CaseRepository(BaseRepository[FraudCase]):
    def __init__(self, session):
        super().__init__(FraudCase, session)

    async def get_with_flags(self, case_id: uuid.UUID, tenant_id: str) -> Optional[FraudCase]:
        # flags relationship is lazy loaded by default, but we can use joinedload if needed
        # For simplicity in this micro-service, we'll assume standard relationship access
        query = select(self.model).where(self.model.id == case_id, self.model.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_open_cases(self, tenant_id: str) -> List[FraudCase]:
        query = select(self.model).where(
            and_(
                self.model.tenant_id == tenant_id,
                self.model.status == CaseStatus.OPEN
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
