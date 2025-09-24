# Логика матчинга (LLM + Qdrant)

from backend.app.config import QdrantCollection, MembersDataType
from backend.app.db.infrastructure.database import QdrantAPI


class MatchingService:
    def __init__(self, qdrant_api: QdrantAPI):
        self.qdrant_api = qdrant_api
        self.candidate_best_matches: list = []
        self.employer_best_matches: list = []

    def find_best_candidates_for_employer(
        self, employer_id: str, top_k=10, alpha=0.7
    ) -> list[tuple]:
        embeddings = self.qdrant_api.client.retrieve(
            collection_name=QdrantCollection.EMPLOYERS.value,
            ids=[employer_id],
            with_vectors=True,
        )[0]

        employer_hard = embeddings.vector.get(MembersDataType.HARD_SKILL.value)
        employer_soft = embeddings.vector.get(MembersDataType.SOFT_SKILL.value)

        # Ищем кандидатов по soft_skill
        soft_skill_results = self.qdrant_api.client.search(
            collection_name=QdrantCollection.CANDIDATES.value,
            query_vector=(MembersDataType.SOFT_SKILL.value, employer_soft),
            limit=100,
            with_vectors=True,
        )

        # Ищем кандидатов по hard_skill
        hard_skill_results = self.qdrant_api.client.search(
            collection_name=QdrantCollection.CANDIDATES.value,
            query_vector=(MembersDataType.HARD_SKILL.value, employer_hard),
            limit=100,
            with_vectors=True,
        )

        # Объединяем результаты по soft_skill и hard_skill
        candidate_scores = {}  # type: ignore[var-annotated]

        for result in soft_skill_results:
            candidate_scores[result.id] = candidate_scores.get(
                result.id, 0
            ) + result.score * (1 - alpha)

        for result in hard_skill_results:
            candidate_scores[result.id] = (
                candidate_scores.get(result.id, 0) + result.score * alpha
            )

        # Сортируем кандидатов по релевантности
        self.candidate_best_matches = sorted(
            candidate_scores.items(), key=lambda x: x[1], reverse=True
        )

        return self.candidate_best_matches[:top_k]

    def find_best_employers_for_candidate(
        self, user_id: str, top_k=10, alpha=0.8
    ) -> list[tuple]:
        embeddings = self.qdrant_api.client.retrieve(
            collection_name=QdrantCollection.CANDIDATES.value,
            ids=[user_id],
            with_vectors=True,
        )[0]

        candidate_hard = embeddings.vector.get(MembersDataType.HARD_SKILL.value)
        candidate_soft = embeddings.vector.get(MembersDataType.SOFT_SKILL.value)

        # Ищем работодателей по soft_skill
        soft_skill_results = self.qdrant_api.client.search(
            collection_name=QdrantCollection.EMPLOYERS.value,
            query_vector=(MembersDataType.SOFT_SKILL.value, candidate_soft),
            limit=100,
            with_vectors=True,
        )

        # Ищем работодателей по hard_skill
        hard_skill_results = self.qdrant_api.client.search(
            collection_name=QdrantCollection.EMPLOYERS.value,
            query_vector=(MembersDataType.HARD_SKILL.value, candidate_hard),
            limit=100,
            with_vectors=True,
        )

        # Объединяем результаты по soft_skill и hard_skill
        employer_scores = {}  # type: ignore[var-annotated]
        for result in soft_skill_results:
            employer_scores[result.id] = employer_scores.get(
                result.id, 0
            ) + result.score * (1 - alpha)

        for result in hard_skill_results:
            employer_scores[result.id] = (
                employer_scores.get(result.id, 0) + result.score * alpha
            )

        # Сортируем работодателей по релевантности
        self.employer_best_matches = sorted(
            employer_scores.items(), key=lambda x: x[1], reverse=True
        )

        return self.employer_best_matches[:top_k]
