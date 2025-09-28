import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, QdrantAPI, qdrant_api
from backend.app.models.employer import EmployerVacancyUpsert, VacancySkill
from backend.app.models.match import MatchSearch, EmployerMatch
from backend.app.services.matching import MatchingService
from backend.app.services.storage import upsert_vacancy

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def modify_vacancy(
    vacancy: EmployerVacancyUpsert,
    skills: list[VacancySkill],
    db: AsyncSession = Depends(get_db),
):
    try:
        new_vacancy = await upsert_vacancy(vacancy, skills, db)
        return new_vacancy
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
async def get_vacancy(id_: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        vacancy = await uow.vacancies.get(id_=id_)
        return vacancy
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.delete("/{id}")
async def delete_vacancy(id_: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            vacancy = await uow.vacancies.get(id_=id_)
            if not vacancy:
                raise HTTPException(status_code=404, detail="Resume not found")
            response = await uow.vacancies.remove(id_=id_)
            await qdrant_api.remove_employer_skills(vacancy.employer_id, vacancy.id)
        return response
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error deleting candidate")


@router.post("/search")
async def search_vacancies(search: MatchSearch):
    """Поиск соискателей по вакансии"""
    try:
        matcher = MatchingService(qdrant_api=QdrantAPI())
        result = await matcher.filter_search(
            soft_query=search.soft_search,
            hard_query=search.hard_search,
            entity_cls=EmployerMatch,
        )

        return result
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
