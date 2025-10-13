# CRUD работодателей
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db, qdrant_api
from backend.app.models.employer import (
    EmployerCreate,
    EmployerResponse,
    EmployerUpdate,
)
from backend.app.services.storage import register_employer

router = APIRouter(prefix="/employers", tags=["employers"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/")
async def create_employer(employer: EmployerCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_employer = await register_employer(employer, db)

        return new_employer
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating employer: {e}")
        raise HTTPException(status_code=500, detail="Error creating employer")


@router.get("/{employer_id}", response_model=EmployerResponse)
async def get_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        employer = await uow.employers.get(id_=employer_id)
        if not employer:
            raise HTTPException(status_code=404, detail="Employer not found")
        return EmployerResponse.model_validate(employer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.patch("/")
async def update_employer(employer: EmployerUpdate, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            new_employer = await uow.employers.update(id_=employer.id, obj=employer)
        return new_employer
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.delete("/{employer_id}")
async def delete_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            vacancies = await uow.vacancies.get_by_employer_id(employer_id)
            await uow.employers.remove(id_=employer_id)
            for vacancy in vacancies:
                await qdrant_api.remove_employer_skills(employer_id, vacancy.id)
    except Exception as e:
        logger.error(f"Error deleting employer: {e}")
        raise HTTPException(status_code=500, detail="Error deleting employer")
