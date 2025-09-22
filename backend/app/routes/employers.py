# CRUD работодателей
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import QdrantCollection
from backend.app.db.infrastructure.database import get_db, qdrant_api
from backend.app.db.infrastructure.members import SqlEmployer
from backend.app.models.employer import EmployerCreate
from backend.app.services.storage import storage_employer

router = APIRouter(tags=["employers"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/employers/")
async def create_employer(employer: EmployerCreate, db: AsyncSession = Depends(get_db)):
    employer_members = SqlEmployer(db)

    try:
        new_employer = await storage_employer(employer_members, db, employer)

        return new_employer
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating employer: {e}")
        raise HTTPException(status_code=500, detail="Error creating employer")


@router.get("/employer/{employer_id}")
async def get_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    employer_members = SqlEmployer(db)
    try:
        return await employer_members.get(id_key=employer_id)
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


@router.get("/employer_vector/{employer_id}")
async def get_employer_vector(employer_id: int, db: AsyncSession = Depends(get_db)):
    employer_members = SqlEmployer(db)
    try:
        employer = await employer_members.get(id_key=employer_id)
        embeddings_hard = qdrant_api.retrieve(
            QdrantCollection.EMPLOYERS.value, [str(employer.user_id)]
        )
        return embeddings_hard
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")
