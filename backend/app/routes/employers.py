# CRUD работодателей
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, qdrant_api
from backend.app.models.auth import TokenData
from backend.app.models.employer import (
    EmployerResponse,
    EmployerUpdate,
)
from backend.app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/employers", tags=["employers"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", response_model=EmployerResponse)
async def get_employer(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Получить данные текущего работодателя"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        logger.info(f"Getting employer for user_id: {current_user.user_id}")
        uow = UnitOfWork(db)
        employer = await uow.employers.get_by_user_id(user_id=current_user.user_id)
        logger.info(f"Employer found: {employer}")

        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        return EmployerResponse.model_validate(employer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting employer: {str(e)}")


@router.patch("/")
async def update_employer(
    employer: EmployerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Обновить данные текущего работодателя"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Получаем работодателя по user_id из токена
        existing_employer = await uow.employers.get_by_user_id(
            user_id=current_user.user_id
        )
        if not existing_employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        # Обновляем только своего работодателя
        async with uow.transaction():
            new_employer = await uow.employers.update(
                id_=existing_employer.id, obj=employer
            )
        return new_employer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employer: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error updating employer: {str(e)}"
        )


@router.delete("/")
async def delete_employer(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Удалить текущего работодателя (каскад по вакансиям, избранному, матчам)"""
    try:
        if not current_user.user_id:
            raise HTTPException(
                status_code=401, detail="Invalid token: user_id missing"
            )

        uow = UnitOfWork(db)
        # Получаем работодателя по user_id из токена
        employer = await uow.employers.get_by_user_id(user_id=current_user.user_id)
        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")

        async with uow.transaction():
            vacancies = await uow.vacancies.get_by_employer_id(employer.id)
            await uow.employers.remove(id_=employer.id)
            for vacancy in vacancies:
                await qdrant_api.remove_employer_skills(employer.id, vacancy.id)

        return {"message": "Employer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employer: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error deleting employer: {str(e)}"
        )
