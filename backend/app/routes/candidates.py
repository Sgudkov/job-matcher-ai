# CRUD кандидатов
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db
from backend.app.models.candidate import (
    CandidateCreate,
    CandidateResumeUpsert,
    ResumeSkill,
)
from backend.app.services.storage import register_candidate, upsert_resume

router = APIRouter(prefix="/candidates", tags=["candidates"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register/")
async def create_candidate(
    candidate: CandidateCreate, db: AsyncSession = Depends(get_db)
):
    try:
        new_candidate = await register_candidate(candidate, db)
        return new_candidate
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(status_code=500, detail="Error creating candidate")


@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            candidate = uow.candidates.get(id_=candidate_id)
            return candidate
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.post("/modify/resume/")
async def modify_resume(
    candidate_resume: CandidateResumeUpsert,
    skills: list[ResumeSkill],
    db: AsyncSession = Depends(get_db),
):
    try:
        new_resume = await upsert_resume(candidate_resume, skills, db)
        return new_resume
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.post("/delete/{candidate_id}")
async def delete_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            await uow.candidates.remove(id_=candidate_id)
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error deleting candidate")
