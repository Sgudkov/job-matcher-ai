# CRUD кандидатов
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import QdrantCollection
from backend.app.db.infrastructure.database import get_db, qdrant_api
from backend.app.db.infrastructure.members import SqlCandidate
from backend.app.models.candidate import CandidateCreate
from backend.app.services.storage import storage_candidate

router = APIRouter(tags=["candidates"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/candidates/")
async def create_candidate(candidate: CandidateCreate, db: AsyncSession = Depends(get_db)):
    candidate_members = SqlCandidate(db)

    try:
        new_candidate = await storage_candidate(candidate_members, db, candidate)

        return new_candidate
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(status_code=500, detail="Error creating candidate")


@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate_members = SqlCandidate(db)
    try:
        return await candidate_members.get(id_key=candidate_id)
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")


@router.get("/candidate_vector/{candidate_id}")
async def get_candidate_vector(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate_members = SqlCandidate(db)
    try:
        candidate = await candidate_members.get(id_key=candidate_id)
        embeddings_hard = qdrant_api.retrieve(QdrantCollection.CANDIDATES_HARD.value, [str(candidate.user_id)])
        return embeddings_hard
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
