from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db.domain.repositories import BaseRepository
from app.db.infrastructure.orm import (
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

    async def get_by_user_id(self, user_id: int):
        """Выбрать пользователя по id"""
        stmt = select(CandidateORM).where(CandidateORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()


class ResumeRepository(BaseRepository[ResumeORM]):
    orm_model = ResumeORM

    async def get_by_candidate_id(self, candidate_id: int):
        """Выбрать кандидата по id"""
        stmt = select(ResumeORM).where(ResumeORM.candidate_id == candidate_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int):
        """Выбрат всех пользователей по id"""
        stmt = select(ResumeORM).where(ResumeORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_resumes_skills(self, user_id: int):
        """Получить все скиллы по резюме"""
        stmt = (
            select(ResumeORM)  # Выбираем только ResumeORM
            .join(CandidateORM)
            .where(CandidateORM.user_id == user_id)
            # Загружаем связанные ResumeSkillORM с помощью selectinload
            .options(selectinload(ResumeORM.skills))
        )
        result = await self.session.execute(stmt)
        # result.scalars().all() вернет список объектов ResumeORM,
        # каждый из которых будет содержать свои связанные объекты ResumeSkillORM
        return result.unique().scalars().all()


class ResumeSkillRepository(BaseRepository[ResumeSkillORM]):
    orm_model = ResumeSkillORM

    async def remove_skills_by_resume_id(self, resume_id: int):
        """Удалить скиллы по id резюме"""
        stmt = delete(ResumeSkillORM).where(ResumeSkillORM.resume_id == resume_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_all_by_resume_id(self, resume_id: int):
        """Получить все резюме по id"""
        stmt = select(ResumeSkillORM).where(ResumeSkillORM.resume_id == resume_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class EmployerRepository(BaseRepository[EmployerORM]):
    orm_model = EmployerORM

    async def get_by_user_id(self, user_id: int):
        """Получить работодателя по user_id"""
        stmt = select(EmployerORM).where(EmployerORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()


class VacancyRepository(BaseRepository[VacancyORM]):
    orm_model = VacancyORM

    async def get_by_employer_id(self, employer_id: int):
        """Получить вакансии по id работодателя"""
        stmt = select(VacancyORM).where(VacancyORM.employer_id == employer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_vacancies_skills(self, user_id: int):
        """Получить скиллы вакансии"""
        stmt = (
            select(VacancyORM)
            .join(EmployerORM)
            .where(EmployerORM.user_id == user_id)
            .options(selectinload(VacancyORM.skills))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()


class VacancySkillRepository(BaseRepository[VacancySkillORM]):
    orm_model = VacancySkillORM

    async def remove_skills_by_vacancy_id(self, vacancy_id: int):
        """Удалить скиллы по вакансии id"""
        stmt = delete(VacancySkillORM).where(VacancySkillORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_skills_by_vacancy_id(self, vacancy_id: int):
        """Получить скиллы по вакансии id"""
        stmt = select(VacancySkillORM).where(VacancySkillORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class MatchRepository(BaseRepository[MatchORM]):
    orm_model = MatchORM

    async def get_by_resume_vacancy(self, resume_id: int, vacancy_id: int):
        """Получить мать для резюме + вакансии"""
        stmt = (
            select(MatchORM)
            .where(MatchORM.resume_id == resume_id)
            .where(MatchORM.vacancy_id == vacancy_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_resumes_by_vacancy_id(self, vacancy_id: int):
        """Получить матч резюме по id вакансии"""
        stmt = select(MatchORM).where(MatchORM.vacancy_id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_vacancies_by_resume_id(self, resume_id: int):
        """Получить матч вакансии по id резюме"""
        stmt = select(MatchORM).where(MatchORM.resume_id == resume_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class UserRepository(BaseRepository[UserORM]):
    orm_model = UserORM

    async def get_by_email(self, email: str):
        """Получить юзера по адресу почты"""
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, id_: int):
        """Получить юзера по id"""
        stmt = select(UserORM).where(UserORM.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
