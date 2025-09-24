from typing import Generic, TypeVar, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.infrastructure.orm import (
    CandidateORM,
    ResumeORM,
    ResumeSkillORM,
    EmployerORM,
    VacancyORM,
    VacancySkillORM,
)

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

    async def remove(self, id_: int) -> bool:
        stmt = delete(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_list(self, id_: int):
        stmt = select(self.orm_model).where(self.orm_model.id == id_)  # type: ignore[union-attr]
        result = await self.session.execute(stmt)
        return result.scalars().all()


class CandidateRepository(BaseRepository[CandidateORM]):
    orm_model = CandidateORM


class ResumeRepository(BaseRepository[ResumeORM]):
    orm_model = ResumeORM


class ResumeSkillRepository(BaseRepository[ResumeSkillORM]):
    orm_model = ResumeSkillORM

    async def remove_skills_by_resume_id(self, resume_id: int):
        stmt = delete(ResumeSkillORM).where(ResumeSkillORM.resume_id == resume_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class EmployerRepository(BaseRepository[EmployerORM]):
    orm_model = EmployerORM


class VacancyRepository(BaseRepository[VacancyORM]):
    orm_model = VacancyORM


class VacancySkillRepository(BaseRepository[VacancySkillORM]):
    orm_model = VacancySkillORM

    async def remove_skills_by_vacancy_id(self, vacancy_id: int):
        stmt = delete(VacancySkillORM).where(VacancySkillORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
