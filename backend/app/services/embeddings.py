# Векторизация
from fastapi import APIRouter

from backend.app.config import SalonDataType
from backend.app.models.candidate import CandidateBase, CandidateEmbedding
from backend.app.utils.embeddings import candidate_embedding_system

router = APIRouter(tags=["vectorization"])


@router.post("/vectorization/", response_model=CandidateEmbedding)
async def vectorize_candidate(candidate: CandidateBase):
    embedding = candidate_embedding_system.vectorize_candidate_data(candidate.soft_skill, SalonDataType.SOFT_SKILL)
    candidate_embedding = CandidateEmbedding(
        **candidate.dict(),
        embedding=embedding
    )
    return candidate_embedding
