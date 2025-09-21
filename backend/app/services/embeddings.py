# Векторизация
from fastapi import APIRouter

from backend.app.config import SalonDataType
from backend.app.models.candidate import CandidateBase, CandidateEmbedding
from backend.app.utils.embeddings import candidate_embedding_system

router = APIRouter(tags=["vectorization"])


@router.post("/vectorization/", response_model=CandidateEmbedding)
async def vectorize_candidate(candidate: CandidateBase):
    embedding_soft = candidate_embedding_system.vectorize_candidate_data(candidate.soft_skill, SalonDataType.SOFT_SKILL)
    embedding_hard = candidate_embedding_system.vectorize_candidate_data(candidate.soft_skill, SalonDataType.HARD_SKILL)

    candidate_embedding = CandidateEmbedding(
        embedding_soft=embedding_soft,
        embedding_hard=embedding_hard
    )
    return candidate_embedding
