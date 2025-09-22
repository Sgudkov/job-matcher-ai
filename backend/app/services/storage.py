# Работа с Qdrant и БД
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import QdrantCollection
from backend.app.db.domain.models import Candidate, Employer
from backend.app.db.infrastructure.database import qdrant_api
from backend.app.db.infrastructure.members import SqlCandidate, SqlEmployer
from backend.app.db.infrastructure.orm import CandidateORM, EmployerORM
from backend.app.models.candidate import (
    CandidateCreate,
    CandidateEmbedding,
    CandidateBase,
)
from backend.app.models.employer import EmployerCreate, EmployerEmbedding, EmployerBase
from backend.app.services.embeddings import vectorize_candidate, vectorize_employer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

for collection in QdrantCollection:
    collection_name = collection.value

    vector_size = 0

    if "soft" in collection_name:
        vector_size = 1024

    if "hard" in collection_name:
        vector_size = 384

    if qdrant_api.client.collection_exists(collection_name):
        continue

    if not qdrant_api.create_collection(collection_name, vector_size):
        logger.error(f"Error creating collection {collection_name}")


async def storage_candidate(
    candidate_member: SqlCandidate, db: AsyncSession, candidate: CandidateCreate
) -> CandidateORM:
    new_candidate = await candidate_member.add(
        candidate=Candidate(
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            phone=str(candidate.phone),
            soft_skill=candidate.soft_skill,
            hard_skill=candidate.hard_skill,
        )
    )

    await db.commit()
    await db.refresh(new_candidate)

    # векторизация
    embedding: CandidateEmbedding = await vectorize_candidate(
        CandidateBase(**new_candidate.__dict__)
    )

    # добавление векторов в Qdrant
    qdrant_api.add_vectors(
        QdrantCollection.CANDIDATES_HARD.value, embedding.embedding_hard
    )
    qdrant_api.add_vectors(
        QdrantCollection.CANDIDATES_SOFT.value, embedding.embedding_soft
    )

    return new_candidate


async def storage_employer(
    employer_member: SqlEmployer, db: AsyncSession, employer: EmployerCreate
) -> EmployerORM:
    new_employer = await employer_member.add(
        employer=Employer(
            first_name=employer.first_name,
            last_name=employer.last_name,
            email=employer.email,
            phone=employer.phone,
            soft_skill=employer.soft_skill,
            hard_skill=employer.hard_skill,
        )
    )

    await db.commit()
    await db.refresh(new_employer)

    # векторизация
    embedding: EmployerEmbedding = await vectorize_employer(
        EmployerBase(**new_employer.__dict__)
    )

    # добавление векторов в Qdrant
    qdrant_api.add_vectors(
        QdrantCollection.EMPLOYERS_HARD.value, embedding.embedding_hard
    )
    qdrant_api.add_vectors(
        QdrantCollection.EMPLOYERS_SOFT.value, embedding.embedding_soft
    )

    return new_employer
