from sqlalchemy import delete, select

from backend.app.db.domain.repositories import BaseRepository
from backend.app.db.infrastructure.orm import (
    ResumeORM,
    ResumeSkillORM,
    EmployerORM,
    VacancyORM,
    VacancySkillORM,
    CandidateORM,
    MatchORM,
    UserORM,
)


class CandidateRepository(BaseRepository[CandidateORM]):
    orm_model = CandidateORM


class ResumeRepository(BaseRepository[ResumeORM]):
    orm_model = ResumeORM

    async def get_by_candidate_id(self, candidate_id: int):
        stmt = select(ResumeORM).where(ResumeORM.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


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

    async def get_by_employer_id(self, employer_id: int):
        stmt = select(VacancyORM).where(VacancyORM.employer_id == employer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class VacancySkillRepository(BaseRepository[VacancySkillORM]):
    orm_model = VacancySkillORM

    async def remove_skills_by_vacancy_id(self, vacancy_id: int):
        stmt = delete(VacancySkillORM).where(VacancySkillORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class MatchRepository(BaseRepository[MatchORM]):
    orm_model = MatchORM

    async def get_by_resume_vacancy(self, resume_id: int, vacancy_id: int):
        stmt = (
            select(MatchORM)
            .where(MatchORM.resume_id == resume_id)
            .where(MatchORM.vacancy_id == vacancy_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_resumes_by_vacancy_id(self, vacancy_id: int):
        stmt = select(MatchORM).where(MatchORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_vacancies_by_resume_id(self, resume_id: int):
        stmt = select(MatchORM).where(MatchORM.resume_id == resume_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class UserRepository(BaseRepository[UserORM]):
    orm_model = UserORM

    async def get_by_email(self, email: str):
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, id_: int):
        stmt = select(UserORM).where(UserORM.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
