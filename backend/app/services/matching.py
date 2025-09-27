# Логика матчинга (LLM + Qdrant)
from datetime import datetime
from typing import TypeVar, Type
from uuid import UUID

from numpy import ndarray
from qdrant_client.http.models import Filter, models
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app import config
from backend.app.config import QdrantCollection, MembersDataType
from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import QdrantAPI, AsyncSessionLocal, engine
from backend.app.db.infrastructure.orm import MatchORM, Base
from backend.app.models.match import (
    CandidateMatchBase,
    EmployerMatchBase,
    MatchCreate,
    MatchSearchFilter,
)
from backend.app.utils.embeddings import MembersEmbeddingSystem

T = TypeVar("T", CandidateMatchBase, EmployerMatchBase)


class MatchingError(Exception):
    """Ошибка при поиске совпадений."""

    pass


class MatchingService:
    def __init__(self, qdrant_api: QdrantAPI):
        self.qdrant_api = qdrant_api
        self.candidate_best_matches: list[CandidateMatchBase] = []
        self.employer_best_matches: list[EmployerMatchBase] = []

    async def find_best_candidates_for_employer(
        self,
        employer_id: int,
        vacancy_id: int,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k=10,
        alpha=0.7,
    ) -> list[CandidateMatchBase]:
        return await self._match_entities(
            source_collection=QdrantCollection.EMPLOYERS.value,
            target_collection=QdrantCollection.CANDIDATES.value,
            source_filter={"employer_id": employer_id, "vacancy_id": vacancy_id},
            entity_cls=CandidateMatchBase,
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
    ) -> list[EmployerMatchBase]:
        return await self._match_entities(
            source_collection=QdrantCollection.CANDIDATES.value,
            target_collection=QdrantCollection.EMPLOYERS.value,
            source_filter={"user_id": user_id, "resume_id": resume_id},
            entity_cls=EmployerMatchBase,
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
        scores: dict[UUID, float] = {}
        matches: dict[UUID, T] = {}

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
                if res.id not in matches:
                    matches[res.id] = entity_cls(**res.payload, id=res.id)
                scores[res.id] = scores.get(res.id, 0) + res.score * alpha / len(
                    hard_vectors
                )

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
                if res.id not in matches:
                    matches[res.id] = entity_cls(**res.payload, id=res.id)
                scores[res.id] = scores.get(res.id, 0) + res.score * (1 - alpha) / len(
                    soft_vectors
                )

        # проставляем итоговые score
        for m in matches.values():
            m.score = scores.get(m.id, 0)

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
                        MatchORM(
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

    async def _filter_search_entities(
        self,
        target_collection: str,
        entity_cls: Type[T],
        soft_vector: ndarray | None = None,
        hard_vector: ndarray | None = None,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k: int = 20,
        alpha: float = 0.8,
    ) -> list[T]:
        """Поиск напрямую по embeddings пользователя (без source_collection)."""

        scores: dict[UUID, float] = {}
        matches: dict[UUID, T] = {}

        # Если не передали ничего, то возвращаем пустой список
        if (
            hard_vector is None
            and soft_vector is None
            and not hard_filter
            and not soft_filter
        ):
            return []

        if (hard_filter or soft_filter) and hard_vector is None and soft_vector is None:
            # Есть только фильтры

            must = []
            must_not = []
            if soft_filter:
                if soft_filter.must:
                    must += soft_filter.must
                if soft_filter.must_not:
                    must_not += soft_filter.must_not

            if hard_filter:
                if hard_filter.must:
                    must += hard_filter.must
                if hard_filter.must_not:
                    must_not += hard_filter.must_not

            # Если передать пустые, то поиск работать не будет
            if not must:
                must = None  # type: ignore[assignment]

            if not must_not:
                must_not = None  # type: ignore[assignment]

            result, _ = self.qdrant_api.client.scroll(
                collection_name=target_collection,
                scroll_filter=Filter(
                    must=must,
                    must_not=must_not,
                ),
                limit=100,
                with_vectors=False,
                with_payload=True,
            )
            for res in result:
                if res.id not in matches:
                    matches[res.id] = entity_cls(**res.payload, id=res.id)
            return list(matches.values())
        else:
            # Есть вектора (и, возможно фильтры)
            if hard_vector is not None:
                # Ищем кандидатов по hard_skill
                result = self.qdrant_api.client.query_points(
                    collection_name=target_collection,
                    query=hard_vector,
                    using=MembersDataType.HARD_SKILL.value,
                    query_filter=hard_filter,
                    limit=100,
                    with_vectors=False,
                    with_payload=True,
                )
                for res in result.points:
                    if res.id not in matches:
                        matches[res.id] = entity_cls(**res.payload, id=res.id)
                    scores[res.id] = scores.get(res.id, 0) + res.score * alpha

            if soft_vector is not None:
                # Ищем работодателей по soft_skill
                result = self.qdrant_api.client.query_points(
                    collection_name=target_collection,
                    query=soft_vector,
                    using=MembersDataType.SOFT_SKILL.value,
                    query_filter=soft_filter,
                    limit=100,
                    with_vectors=False,
                    with_payload=True,
                )
                for res in result.points:
                    if res.id not in matches:
                        matches[res.id] = entity_cls(**res.payload, id=res.id)
                    scores[res.id] = scores.get(res.id, 0) + res.score * (1 - alpha)

        # проставляем итоговые score
        for m in matches.values():
            m.score = scores.get(m.id, 0)

        return sorted(matches.values(), key=lambda x: x.score, reverse=True)[:top_k]

    async def filter_search(
        self,
        source_filter: dict,
        db: AsyncSession,
        soft_query: MatchSearchFilter,
        hard_query: MatchSearchFilter,
        entity_cls: Type[T],
    ) -> list[T]:
        """Поиск соответствующих работодателей/кандидатов"""

        uow = UnitOfWork(db)

        # проверим, что записи есть в БД
        match entity_cls:
            case cls if cls is CandidateMatchBase:
                vacancy_id = source_filter.get("vacancy_id", None)
                target_collection = QdrantCollection.CANDIDATES.value
                if not await uow.vacancies.get(vacancy_id):
                    raise MatchingError("Search resumes: Vacancy not found")
            case cls if cls is EmployerMatchBase:
                resume_id = source_filter.get("resume_id", None)
                target_collection = QdrantCollection.EMPLOYERS.value
                if not await uow.resumes.get(resume_id):
                    raise MatchingError("Search resumes: Resume not found")
            case _:
                raise MatchingError("Search resumes: Entity not found")

        soft_filter = Filter(must=[], must_not=[], should=[])
        hard_filter = Filter(must=[], must_not=[], should=[])

        # Соберем фильтры

        if hard_query.must_have:
            hard_filter.must = [
                (
                    models.FieldCondition(
                        key=MembersDataType.SKILL_NAME.value,
                        match=models.MatchAny(any=[s for s in hard_query.must_have]),
                    )
                )
            ]

        if soft_query.must_have:
            soft_filter.must = [
                (
                    models.FieldCondition(
                        key=MembersDataType.SUMMARY.value,
                        match=models.MatchAny(any=[s for s in soft_query.must_have]),
                    )
                )
            ]

        if hard_query.must_not_have:
            hard_filter.must_not = [
                (
                    models.FieldCondition(
                        key=MembersDataType.SKILL_NAME.value,
                        match=models.MatchAny(
                            any=[s for s in hard_query.must_not_have]
                        ),
                    )
                )
            ]

        if soft_query.must_not_have:
            soft_filter.must_not = [
                (
                    models.FieldCondition(
                        key=MembersDataType.SUMMARY.value,
                        match=models.MatchAny(
                            any=[s for s in soft_query.must_not_have]
                        ),
                    )
                )
            ]

        text_hard = " ".join(
            [
                " ".join([s.lower() for s in hard_query.must_have] or []),
                " ".join([s.lower() for s in hard_query.should_have] or []),
            ]
        ).strip()

        text_soft = " ".join(
            [
                " ".join([s.lower() for s in soft_query.must_have] or []),
                " ".join([s.lower() for s in soft_query.should_have] or []),
            ]
        ).strip()

        if text_soft:
            soft_vector = MembersEmbeddingSystem.encode_long_text(
                model=config.SOFT_MODEL, text=text_soft
            )
        else:
            soft_vector = None

        if text_hard:
            hard_vector = MembersEmbeddingSystem.encode_long_text(
                model=config.HARD_MODEL, text=text_hard
            )
        else:
            hard_vector = None

        if not hard_filter.must and not hard_filter.must_not:
            hard_filter = None

        if not soft_filter.must and not soft_filter.must_not:
            soft_filter = None

        return await self._filter_search_entities(
            target_collection=target_collection,
            entity_cls=entity_cls,
            soft_vector=soft_vector,
            hard_vector=hard_vector,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
        )


async def match():
    matcher = MatchingService(qdrant_api=QdrantAPI())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

    try:
        async with AsyncSessionLocal() as db:
            result = await matcher.filter_search(
                source_filter={"resume_id": 0},
                db=db,
                soft_query=MatchSearchFilter(),
                hard_query=MatchSearchFilter(must_have=["Бард"]),
                entity_cls=CandidateMatchBase,
            )
            print(result)
            # await matcher.recalc_matches_for_vacancy(employer_id=0, vacancy_id=0, db=db)
    except Exception as e:
        print("Error matching: ", e)


if __name__ == "__main__":
    import asyncio

    asyncio.run(match())
