from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.repositories import (
    CandidateRepository,
    ResumeRepository,
    ResumeSkillRepository,
    EmployerRepository,
    VacancyRepository,
    VacancySkillRepository,
)


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Репозитории
        self.candidates = CandidateRepository(session)
        self.resumes = ResumeRepository(session)
        self.resume_skills = ResumeSkillRepository(session)
        self.employers = EmployerRepository(session)
        self.vacancies = VacancyRepository(session)
        self.vacancy_skills = VacancySkillRepository(session)

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
