import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, QdrantAPI, qdrant_api
from backend.app.models.candidate import ResumeUpsert, ResumeSkillBase
from backend.app.models.filter import SearchRequest

from backend.app.models.match import CandidateMatch
from backend.app.services.fiter import SearchFilter
from backend.app.services.storage import upsert_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def modify_resume(
    candidate_resume: ResumeUpsert,
    skills: list[ResumeSkillBase],
    db: AsyncSession = Depends(get_db),
):
    """ "Создать резюме (по candidate_id)"""
    try:
        new_resume = await upsert_resume(candidate_resume, skills, db)
        return new_resume
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.get("/{id}")
async def get_resumes(id_: int, db: AsyncSession = Depends(get_db)):
    """Получить данные соискателя"""
    try:
        uow = UnitOfWork(db)
        resume = await uow.resumes.get(id_=id_)
        return resume
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.delete("/{id}")
async def delete_resume(id_: int, db: AsyncSession = Depends(get_db)):
    """Удалить резюме (каскад: матчи, избранное)"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            resume = await uow.resumes.get(id_)
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            response = await uow.resumes.remove(id_=resume.id)
            await qdrant_api.remove_candidate_skills(resume.candidate_id, resume.id)
        return response
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error deleting candidate")


@router.post("/search")
async def search_resumes(search: SearchRequest):
    """Поиск соискателей по вакансии"""
    try:
        matcher = SearchFilter(qdrant_api=QdrantAPI(), entity_cls=CandidateMatch)
        result = await matcher.filter_search(
            search_request=search,
        )

        return result
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
