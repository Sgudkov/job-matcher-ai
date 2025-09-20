# CRUD кандидатов
from fastapi import APIRouter

from backend.app.models.candidate import CandidateBase
from backend.app.services.embeddings import vectorize_candidate

router = APIRouter(tags=["candidates"])


@router.post("/candidates/")
async def create_candidate(candidate: CandidateBase):
    embedding = await vectorize_candidate(candidate)

    return embedding
