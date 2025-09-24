# Векторизация
from fastapi import APIRouter

from backend.app.models.candidate import CandidateEmbedding, CandidateVector
from backend.app.models.employer import EmployerEmbedding, EmployerVector
from backend.app.utils.embeddings import members_embedding_system

router = APIRouter(tags=["candidate_vectorization", "employer_vectorization"])


@router.post("/candidate_vectorization/", response_model=CandidateEmbedding)
async def vectorize_candidate(candidate: CandidateVector):
    embeddings = members_embedding_system.vectorize_candidate_data(candidate)

    candidate_embedding = CandidateEmbedding(embeddings=embeddings)
    return candidate_embedding


@router.post("/employer_vectorization/", response_model=EmployerEmbedding)
async def vectorize_employer(employer: EmployerVector):
    embeddings = members_embedding_system.vectorize_employer_data(employer)

    employer_embedding = EmployerEmbedding(embeddings=embeddings)
    return employer_embedding
