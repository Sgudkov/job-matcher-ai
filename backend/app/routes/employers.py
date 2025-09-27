# CRUD работодателей
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db
from backend.app.models.employer import (
    EmployerCreate,
    EmployerVacancyUpsert,
    VacancySkill,
)
from backend.app.services.storage import register_employer, upsert_vacancy

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


@router.get("/{employer_id}")
async def get_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        employer = await uow.employers.get(id_=employer_id)
        return employer
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.get("/vector/{employer_id}")
async def get_employer_vector(employer_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        employer = await uow.employers.get(id_=employer_id)
        return employer
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.post("/modify/vacancy/")
async def modify_vacancy(
    employer_vacancy: EmployerVacancyUpsert,
    skills: list[VacancySkill],
    db: AsyncSession = Depends(get_db),
):
    try:
        new_vacancy = await upsert_vacancy(employer_vacancy, skills, db)
        return new_vacancy
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.post("/delete/{employer_id}")
async def delete_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            await uow.employers.remove(id_=employer_id)
    except Exception as e:
        logger.error(f"Error deleting employer: {e}")
        raise HTTPException(status_code=500, detail="Error deleting employer")
