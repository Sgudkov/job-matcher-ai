# Векторизация
from fastapi import APIRouter

from backend.app.config import MembersDataType
from backend.app.models.candidate import CandidateBase, CandidateEmbedding
from backend.app.models.employer import EmployerEmbedding, EmployerBase
from backend.app.utils.embeddings import members_embedding_system

router = APIRouter(tags=["candidate_vectorization", "employer_vectorization"])


@router.post("/candidate_vectorization/", response_model=CandidateEmbedding)
async def vectorize_candidate(candidate: CandidateBase):
    embedding_soft = members_embedding_system.vectorize_candidate_data(
        candidate, MembersDataType.SOFT_SKILL
    )
    embedding_hard = members_embedding_system.vectorize_candidate_data(
        candidate, MembersDataType.HARD_SKILL
    )

    candidate_embedding = CandidateEmbedding(
        embedding_soft=embedding_soft, embedding_hard=embedding_hard
    )
    return candidate_embedding


@router.post("/employer_vectorization/", response_model=EmployerEmbedding)
async def vectorize_employer(employer: EmployerBase):
    embedding_soft = members_embedding_system.vectorize_employer_data(
        employer, MembersDataType.SOFT_SKILL
    )
    embedding_hard = members_embedding_system.vectorize_employer_data(
        employer, MembersDataType.HARD_SKILL
    )

    employer_embedding = EmployerEmbedding(
        embedding_soft=embedding_soft, embedding_hard=embedding_hard
    )
    return employer_embedding
