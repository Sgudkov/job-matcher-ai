# CRUD кандидатов
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, qdrant_api
from backend.app.models.auth import TokenData
from backend.app.models.candidate import (
    CandidateResponse,
    CandidateUpdate,
)
from backend.app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/candidates", tags=["candidates"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", response_model=CandidateResponse)
async def get_candidate(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Получить данные соискателя"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        logger.info(f"Getting candidate for user_id: {current_user.user_id}")
        uow = UnitOfWork(db)
        candidate = await uow.candidates.get_by_user_id(user_id=current_user.user_id)
        logger.info(f"Candidate found: {candidate}")

        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        return CandidateResponse.model_validate(candidate)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting candidate: {str(e)}"
        )


@router.patch("/")
async def update_candidate(
    candidate: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Обновить данные текущего соискателя"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Получаем кандидата по user_id из токена
        existing_candidate = await uow.candidates.get_by_user_id(
            user_id=current_user.user_id
        )
        if not existing_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Обновляем только своего кандидата
        async with uow.transaction():
            new_candidate = await uow.candidates.update(
                id_=existing_candidate.id, obj=candidate
            )
        return new_candidate
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating candidate: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error updating candidate: {str(e)}"
        )


@router.delete("/")
async def delete_candidate(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Удалить текущего соискателя (каскад по резюме, избранному, матчам)"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Получаем кандидата по user_id из токена
        candidate = await uow.candidates.get_by_user_id(user_id=current_user.user_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        async with uow.transaction():
            resumes = await uow.resumes.get_by_candidate_id(candidate.id)
            await uow.candidates.remove(id_=candidate.id)
            for resume in resumes:
                await qdrant_api.remove_candidate_skills(candidate.id, resume.id)

        return {"message": "Candidate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error deleting candidate: {str(e)}"
        )
