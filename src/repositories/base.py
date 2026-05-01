from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import uuid

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any, tenant_id: str) -> Optional[T]:
        query = select(self.model).where(self.model.id == id, self.model.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, limit: int = 100, offset: int = 0) -> List[T]:
        query = select(self.model).where(self.model.tenant_id == tenant_id).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: Any, tenant_id: str, **kwargs) -> Optional[T]:
        query = (
            update(self.model)
            .where(self.model.id == id, self.model.tenant_id == tenant_id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, id: Any, tenant_id: str) -> bool:
        query = delete(self.model).where(self.model.id == id, self.model.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.rowcount > 0
