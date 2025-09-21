# CRUD кандидатов
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.models import Candidate
from backend.app.db.infrastructure.database import get_db
from backend.app.db.infrastructure.members import SqlCandidate
from backend.app.models.candidate import CandidateEmbedding, CandidateCreate
from backend.app.services.embeddings import vectorize_candidate

router = APIRouter(tags=["candidates"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/candidates/")
async def create_candidate(candidate: CandidateCreate, db: AsyncSession = Depends(get_db)):
    embedding: CandidateEmbedding = await vectorize_candidate(candidate)
    candidate_members = SqlCandidate(db)

    try:
        new_candidate = await candidate_members.add(
            candidate=Candidate(
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                email=candidate.email,
                phone=candidate.phone,
                soft_skill=candidate.soft_skill,
                hard_skill=candidate.hard_skill,
                embedding_soft=embedding.embedding_soft,
                embedding_hard=embedding.embedding_hard
            )
        )

        await db.commit()
        await db.refresh(new_candidate)
        return new_candidate
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {e}")
        raise HTTPException(status_code=500, detail="Error creating candidate")


@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    candidate_members = SqlCandidate(db)
    try:
        return await candidate_members.get(user_id=candidate_id)
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
