import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, QdrantAPI, qdrant_api
from backend.app.models.auth import TokenData
from backend.app.models.employer import (
    EmployerVacancyUpsert,
    VacancySkill,
    VacancyBase,
    EmployerBase,
    VacancyResponse,
)
from backend.app.models.filter import SearchRequest
from backend.app.models.match import EmployerMatch
from backend.app.services.dependencies import get_current_active_user
from backend.app.services.fiter import SearchFilter
from backend.app.services.storage import upsert_vacancy

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def modify_vacancy(
    vacancy: EmployerVacancyUpsert,
    skills: list[VacancySkill],
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Создать вакансию для текущего работодателя"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Проверяем, что работодатель существует и принадлежит текущему пользователю
        employer = await uow.employers.get_by_user_id(user_id=current_user.user_id)
        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        # Устанавливаем employer_id из токена, игнорируя переданный
        vacancy.employer_id = employer.id

        new_vacancy = await upsert_vacancy(vacancy, skills, db)
        return new_vacancy
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating vacancy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating vacancy: {str(e)}")


@router.get("/{id_}")
async def get_vacancy(
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Получить вакансию по ID"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        vacancy_orm = await uow.vacancies.get(id_=id_)
        if not vacancy_orm:
            raise HTTPException(status_code=404, detail="Vacancy not found")

        vacancy = VacancyBase.model_validate(vacancy_orm.__dict__)

        employer = await uow.employers.get(id_=vacancy.employer_id)

        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        employer = EmployerBase.model_validate(employer.__dict__)

        skills_data = await uow.vacancy_skills.get_skills_by_vacancy_id(vacancy.id)
        skills = [VacancySkill.model_validate(skill) for skill in skills_data]
        response = VacancyResponse(
            vacancy_description=vacancy, employer=employer, skills=skills
        )

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vacancy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting vacancy: {str(e)}")


@router.delete("/{id}")
async def delete_vacancy(
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Удалить вакансию (каскад: матчи, избранное) - только свою"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        vacancy = await uow.vacancies.get(id_=id_)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")

        # Проверяем, что вакансия принадлежит текущему пользователю
        employer = await uow.employers.get_by_user_id(user_id=current_user.user_id)
        if not employer or vacancy.employer_id != employer.id:
            raise HTTPException(
                status_code=403, detail="Access denied: not your vacancy"
            )

        async with uow.transaction():
            await uow.vacancies.remove(id_=id_)
            await qdrant_api.remove_employer_skills(vacancy.employer_id, vacancy.id)

        return {"message": "Vacancy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vacancy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting vacancy: {str(e)}")


@router.post("/search")
async def search_vacancies(search: SearchRequest):
    """Поиск вакансий по резюме"""
    try:
        matcher = SearchFilter(qdrant_api=QdrantAPI(), entity_cls=EmployerMatch)
        # Получаем внутренние модели с векторами
        raw_matches = await matcher.filter_search(
            search_request=search,
        )

        # Агрегируем данные: объединяем soft + hard векторы в единый ответ
        aggregated_results = matcher.aggregate_vacancy_matches(raw_matches)

        return aggregated_results
    except Exception as e:
        logger.error(f"Error searching vacancies: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error searching vacancies: {str(e)}"
        )
