# Логика матчинга (LLM + Qdrant)
from backend.app.db.domain.members import CandidateMembers, EmployerMembers
from backend.app.db.infrastructure.database import QdrantAPI


class MatchingService:
    def __init__(
        self,
        candidate: CandidateMembers,
        employer: EmployerMembers,
        qdrant_api: QdrantAPI,
    ):
        self.candidate = candidate
        self.employer = employer
        self.qdrant_api = qdrant_api

    def candidate_match(self):
        # TODO
        # embedding_hard = candidate.embedding_hard
        # embedding_soft = candidate.embedding_soft
        # recommend_employers = qdrant_api.search(QdrantCollection.EMPLOYERS_HARD.value, embedding_hard, 50)
        pass
