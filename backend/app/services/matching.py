# Логика матчинга (LLM + Qdrant)
from datetime import datetime
from typing import TypeVar, Type

from qdrant_client.http.models import Filter
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import QdrantCollection, MembersDataType
from app.db.domain.unit_of_work import UnitOfWork
from app.db.infrastructure.database import QdrantAPI
from app.models.match import (
    MatchCreate,
    CandidateMatch,
    EmployerMatch,
)

T = TypeVar("T", EmployerMatch, CandidateMatch)


class MatchingError(Exception):
    """Ошибка при поиске совпадений."""

    pass


class MatchingService:
    def __init__(self, qdrant_api: QdrantAPI):
        self.qdrant_api = qdrant_api
        self.candidate_best_matches: list[CandidateMatch] = []
        self.employer_best_matches: list[EmployerMatch] = []

    async def find_best_candidates_for_employer(
        self,
        employer_id: int,
        vacancy_id: int,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k=10,
        alpha=0.7,
    ) -> list[CandidateMatch]:
        return await self._match_entities(
            source_collection=QdrantCollection.EMPLOYERS.value,
            target_collection=QdrantCollection.CANDIDATES.value,
            source_filter={"employer_id": employer_id, "vacancy_id": vacancy_id},
            entity_cls=CandidateMatch,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
            top_k=top_k,
            alpha=alpha,
        )

    async def find_best_employers_for_candidate(
        self,
        user_id: int,
        resume_id: int,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k=10,
        alpha=0.8,
    ) -> list[EmployerMatch]:
        return await self._match_entities(
            source_collection=QdrantCollection.CANDIDATES.value,
            target_collection=QdrantCollection.EMPLOYERS.value,
            source_filter={"user_id": user_id, "resume_id": resume_id},
            entity_cls=EmployerMatch,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
            top_k=top_k,
            alpha=alpha,
        )

    async def _collect_vectors(self, points):
        """Достаем вектора скилов"""
        hard, soft = [], []
        for result in points:
            payload = result.payload
            match payload.get("type", ""):
                case MembersDataType.HARD_SKILL.value:
                    hard.append(result.vector.get(MembersDataType.HARD_SKILL.value, []))
                case MembersDataType.SOFT_SKILL.value:
                    soft.append(result.vector.get(MembersDataType.SOFT_SKILL.value, []))
        return hard, soft

    async def _match_entities(
        self,
        source_collection: str,
        target_collection: str,
        source_filter: dict,
        entity_cls: Type[T],
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k=10,
        alpha=0.8,
    ) -> list[T]:
        """Универсальный метод для поиска совпадений (candidates <-> employers)"""

        # достаём entity (работодатель или кандидат)
        # нужны embeddings для матча
        source_points = self.qdrant_api.scroll(
            collection_name=source_collection,
            limit=20,
            **source_filter,
        )

        if not source_points:
            raise MatchingError(
                f"Matching error: source entity {type(entity_cls)} not found"
            )

        # берём первую запись (ожидаем что это нужная вакансия/резюме)
        hard_vectors, soft_vectors = await self._collect_vectors(source_points[0])
        if not hard_vectors or not soft_vectors:
            raise MatchingError(
                "Matching error: Entity does not have both hard and soft skills"
            )

        # результаты поиска
        scores: dict[str, float] = {}
        matches: dict[str, T] = {}
        search_counter = {}

        # ищем по hard skills
        for hard in hard_vectors:
            result = self.qdrant_api.client.query_points(
                collection_name=target_collection,
                query=hard,
                using=MembersDataType.HARD_SKILL.value,
                query_filter=hard_filter,
                limit=100,
                with_vectors=False,
                with_payload=True,
            )
            for res in result.points:
                complex_key = await entity_cls(**res.payload).get_complex_key()
                if complex_key not in matches:
                    matches[complex_key] = entity_cls(**res.payload, id=complex_key)
                    search_counter[complex_key] = 0
                scores[complex_key] = scores.get(complex_key, 0) + res.score * alpha
                search_counter[complex_key] += 1

        # ищем по soft skills
        for soft in soft_vectors:
            # Ищем работодателей по soft_skill
            result = self.qdrant_api.client.query_points(
                collection_name=target_collection,
                query=soft,
                using=MembersDataType.SOFT_SKILL.value,
                query_filter=soft_filter,
                limit=100,
                with_vectors=False,
                with_payload=True,
            )
            for res in result.points:
                complex_key = await entity_cls(**res.payload).get_complex_key()
                if complex_key not in matches:
                    matches[complex_key] = entity_cls(**res.payload, id=complex_key)
                    search_counter[complex_key] = 0
                scores[complex_key] = scores.get(complex_key, 0) + res.score * (
                    1 - alpha
                )
                search_counter[complex_key] += 1

        # проставляем итоговые score
        for m in matches.values():
            m.score = scores.get(m.id, 0)
            # Усредним оценку, чтобы не было перекосов, если у кого одних векторов больше чем других
            if search_counter[m.id] > 0:
                m.score /= search_counter[m.id]

        # сортировка и top_k
        return sorted(matches.values(), key=lambda x: x.score, reverse=True)[:top_k]

    async def recalc_matches_for_resume(
        self, resume_id: int, user_id: int, db: AsyncSession
    ):
        uow = UnitOfWork(db)

        # получаем лучших работодателей
        best_employers = await self.find_best_employers_for_candidate(
            top_k=10, alpha=0.8, user_id=user_id, resume_id=resume_id
        )

        async with uow.transaction():
            for employer in best_employers:
                match_ = await uow.matches.get_by_resume_vacancy(
                    vacancy_id=employer.vacancy_id, resume_id=resume_id
                )
                if match_:
                    if abs(match_.score - employer.score) > 0.01:
                        match_.score = employer.score
                        match_.is_new = True
                else:
                    await uow.matches.add(
                        MatchCreate(
                            resume_id=resume_id,
                            vacancy_id=employer.vacancy_id,
                            score=employer.score,
                            updated_at=datetime.now(),
                            is_new=True,
                        )
                    )

    async def recalc_matches_for_vacancy(
        self, employer_id: int, vacancy_id: int, db: AsyncSession
    ):
        uow = UnitOfWork(db)

        # получаем лучших кандидатов
        best_candidates = await self.find_best_candidates_for_employer(
            top_k=10, alpha=0.8, employer_id=employer_id, vacancy_id=vacancy_id
        )

        async with uow.transaction():
            for candidate in best_candidates:
                match_ = await uow.matches.get_by_resume_vacancy(
                    vacancy_id=vacancy_id, resume_id=candidate.resume_id
                )
                if match_:
                    if abs(match_.score - candidate.score) > 0.05:
                        match_.score = candidate.score
                        match_.is_new = True
                else:
                    new_match = MatchCreate(
                        resume_id=candidate.resume_id,
                        vacancy_id=vacancy_id,
                        score=candidate.score,
                        is_new=True,
                    )
                    await uow.matches.add(new_match)


# async def match():
#     matcher = MatchingService(qdrant_api=QdrantAPI())
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     await engine.dispose()
#
#     try:
#         async with AsyncSessionLocal() as db:
#             result = await matcher.filter_search(
#                 soft_query=MatchSearchFilter(),
#                 hard_query=MatchSearchFilter(must_have=["Бард"]),
#                 entity_cls=CandidateMatch,
#             )
#             print(result)
#             # await matcher.recalc_matches_for_vacancy(employer_id=0, vacancy_id=0, db=db)
#     except Exception as e:
#         print("Error matching: ", e)
#
#
# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.run(match())
