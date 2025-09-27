# CRUD кандидатов
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db
from backend.app.models.candidate import (
    CandidateCreate,
    CandidateUpdate,
)
from backend.app.services.storage import register_candidate

router = APIRouter(prefix="/candidates", tags=["candidates"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def create_candidate(
    candidate: CandidateCreate, db: AsyncSession = Depends(get_db)
):
    """Создать соискателя"""
    try:
        new_candidate = await register_candidate(candidate, db)
        return new_candidate
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(status_code=500, detail="Error creating candidate")


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Получить данные соискателя"""
    try:
        uow = UnitOfWork(db)
        candidate = await uow.candidates.get(id_=candidate_id)
        return candidate
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.patch("/")
async def update_candidate(
    candidate: CandidateUpdate, db: AsyncSession = Depends(get_db)
):
    """Обновить данные соискателя"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            if not await uow.candidates.get(id_=candidate.id):
                raise HTTPException(status_code=404, detail="Candidate not found")
            result = await uow.candidates.update(candidate)
        return result
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить соискателя (каскад по резюме, избранному, матчам)"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            await uow.candidates.remove(id_=candidate_id)
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error deleting candidate")
