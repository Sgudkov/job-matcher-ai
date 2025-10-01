from typing import Generic, TypeVar, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    orm_model: Optional[type[T]] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, obj) -> T:
        orm_obj = self.orm_model(**obj.dict())  # type: ignore[misc]
        self.session.add(orm_obj)
        return orm_obj

    async def get(self, id_: int) -> T | None:
        stmt = select(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, id_: int, obj) -> T | None:
        stmt = select(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            for key, value in obj.dict().items():
                setattr(orm_obj, key, value)
        return orm_obj

    async def remove(self, id_: int) -> bool:
        stmt = delete(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_list(self, id_: int):
        stmt = select(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all(self):
        stmt = select(self.orm_model)
        result = await self.session.execute(stmt)
        return result.scalars().all()
