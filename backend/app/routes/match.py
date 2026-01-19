# Эндпоинт для поиска матчей
import logging

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.domain.unit_of_work import UnitOfWork
from app.db.infrastructure.database import get_db, QdrantAPI
from app.services.matching import MatchingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["matches"])
recalc_router = APIRouter(prefix="/recalc", tags=["recalc"])


@router.get("/resumes/{resume_id}")
async def get_resume_matches(resume_id: int, db: AsyncSession = Depends(get_db)):
    """Получить матс резюме"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            result = await uow.matches.get_vacancies_by_resume_id(resume_id=resume_id)
        return result
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.get("/vacancies/{vacancy_id}")
async def get_vacancy_matches(vacancy_id: int, db: AsyncSession = Depends(get_db)):
    """Получить матчи для вакансии"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            result = await uow.matches.get_resumes_by_vacancy_id(vacancy_id=vacancy_id)
        return result
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@recalc_router.post("/matches/vacancy/")
async def recalc_resumes(
    employer_id: int, vacancy_id: int, db: AsyncSession = Depends(get_db)
):
    """Пересчитать матчи для соискателя"""
    try:
        matcher = MatchingService(qdrant_api=QdrantAPI())
        await matcher.recalc_matches_for_vacancy(
            employer_id=employer_id, vacancy_id=vacancy_id, db=db
        )

    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@recalc_router.post("/matches/resume/")
async def recalc_vacancies(
    resume_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    """Пересчитать матчи для вакансии"""
    try:
        matcher = MatchingService(qdrant_api=QdrantAPI())
        await matcher.recalc_matches_for_resume(
            resume_id=resume_id, user_id=user_id, db=db
        )

    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
