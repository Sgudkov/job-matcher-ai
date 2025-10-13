import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, QdrantAPI, qdrant_api
from backend.app.models.auth import TokenData
from backend.app.models.candidate import ResumeUpsert, ResumeSkillBase
from backend.app.models.filter import SearchRequest

from backend.app.models.match import CandidateMatch
from backend.app.services.dependencies import get_current_active_user
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
    current_user: TokenData = Depends(get_current_active_user),
):
    """Создать резюме для текущего кандидата"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Проверяем, что кандидат существует и принадлежит текущему пользователю
        candidate = await uow.candidates.get_by_user_id(user_id=current_user.user_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Устанавливаем candidate_id из токена, игнорируя переданный
        candidate_resume.candidate_id = candidate.id

        new_resume = await upsert_resume(candidate_resume, skills, db)
        return new_resume
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating resume: {str(e)}")


@router.get("/{id}")
async def get_resumes(
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Получить резюме по ID (только свое)"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        resume = await uow.resumes.get(id_=id_)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Проверяем, что резюме принадлежит текущему пользователю
        candidate = await uow.candidates.get_by_user_id(user_id=current_user.user_id)
        if not candidate or resume.candidate_id != candidate.id:
            raise HTTPException(
                status_code=403, detail="Access denied: not your resume"
            )

        return resume
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting resume: {str(e)}")


@router.delete("/{id}")
async def delete_resume(
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Удалить резюме (каскад: матчи, избранное) - только свое"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        resume = await uow.resumes.get(id_)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Проверяем, что резюме принадлежит текущему пользователю
        candidate = await uow.candidates.get_by_user_id(user_id=current_user.user_id)
        if not candidate or resume.candidate_id != candidate.id:
            raise HTTPException(
                status_code=403, detail="Access denied: not your resume"
            )

        async with uow.transaction():
            await uow.resumes.remove(id_=resume.id)
            await qdrant_api.remove_candidate_skills(resume.candidate_id, resume.id)

        return {"message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")


@router.post("/search")
async def search_resumes(search: SearchRequest):
    """Поиск соискателей по вакансии"""
    try:
        matcher = SearchFilter(qdrant_api=QdrantAPI(), entity_cls=CandidateMatch)
        # Получаем внутренние модели с векторами
        raw_matches = await matcher.filter_search(
            search_request=search,
        )

        # Агрегируем данные: объединяем soft + hard векторы в единый ответ
        aggregated_results = matcher.aggregate_resume_matches(raw_matches)

        return aggregated_results
    except Exception as e:
        logger.error(f"Error searching resumes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error searching resumes: {str(e)}"
        )
