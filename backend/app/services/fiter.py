from typing import TypeVar, Type, Tuple

from numpy import ndarray
from qdrant_client.http.models import Filter, models

from backend.app import config
from backend.app.config import MembersDataType, QdrantCollection
from backend.app.db.infrastructure.database import QdrantAPI
from backend.app.models.filter import SearchRequest
from backend.app.models.match import EmployerMatch, CandidateMatch
from backend.app.utils.embeddings import MembersEmbeddingSystem

T = TypeVar("T", EmployerMatch, CandidateMatch)


class SearchError(Exception):
    """Ошибка при поиске совпадений."""

    pass


class SearchFilter:
    def __init__(self, qdrant_api: QdrantAPI, entity_cls: Type[T]):
        self.qdrant_api = qdrant_api
        self.entity_cls: Type[T] = entity_cls

    async def _filter_search_entities(
        self,
        target_collection: str,
        soft_vector: ndarray | None = None,
        hard_vector: ndarray | None = None,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        top_k: int = 20,
        alpha: float = 0.8,
    ) -> list[T]:
        """Поиск напрямую по embeddings пользователя (без source_collection)."""

        scores: dict[str, float] = {}
        matches: dict[str, T] = {}
        search_counter = {}

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
                    matches[res.id] = self.entity_cls(**res.payload, id=res.id)  # type: ignore[call-arg]
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
                        matches[res.id] = self.entity_cls(**res.payload, id=res.id)  # type: ignore[call-arg]
                        search_counter[res.id] = 0
                    scores[res.id] = scores.get(res.id, 0) + res.score * alpha
                    search_counter[res.id] += 1

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
                        matches[res.id] = self.entity_cls(**res.payload, id=res.id)  # type: ignore[call-arg]
                        search_counter[res.id] = 0
                    scores[res.id] = scores.get(res.id, 0) + res.score * (1 - alpha)
                    search_counter[res.id] += 1

        # проставляем итоговые score
        for m in matches.values():
            m.score = scores.get(m.id, 0)
            # Усредним оценку, чтобы не было перекосов, если у кого одних векторов больше чем других
            if search_counter[m.id] > 0:
                m.score /= search_counter[m.id]

        return sorted(matches.values(), key=lambda x: x.score, reverse=True)[:top_k]

    async def _build_qdrant_filters(
        self, search_request: SearchRequest
    ) -> Tuple[Filter | None, Filter | None, ndarray | None, ndarray | None]:
        soft_skills_must = []
        soft_skills_should = []
        soft_skills_must_not = []

        hard_skills_must = []
        hard_skills_should = []
        hard_skills_must_not = []
        filters = search_request.filters

        # Векторизуем hard и soft скиллы

        text_hard = " ".join(
            [
                " ".join([s.lower() for s in filters.skills.must_have] or []),  # type: ignore[union-attr]
                " ".join([s.lower() for s in filters.skills.should_have] or []),  # type: ignore[union-attr]
            ]
        ).strip()

        text_soft = " ".join(
            [
                " ".join([s.lower() for s in filters.summary.must_have] or []),  # type: ignore[union-attr]
                " ".join([s.lower() for s in filters.summary.should_have] or []),  # type: ignore[union-attr]
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

        # Соберем фильтры

        # 1 Hard skills фильтры
        if filters.skills:
            if filters.skills.must_have:
                hard_skills_must.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.must_have
                    ]
                )

            if filters.skills.must_not_have:
                hard_skills_must_not.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.must_not_have
                    ]
                )

            if filters.skills.should_have:
                hard_skills_should.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.should_have
                    ]
                )

        # 2 Soft skills фильтры

        # Summary
        if filters.summary:
            if filters.summary.must_have:
                soft_skills_must.extend(
                    [
                        models.FieldCondition(
                            key="summary_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.summary.must_have
                    ]
                )

            if filters.summary.must_not_have:
                soft_skills_must_not.extend(
                    [
                        models.FieldCondition(
                            key="summary_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.summary.must_not_have
                    ]
                )

            if filters.summary.should_have:
                soft_skills_should.extend(
                    [
                        models.FieldCondition(
                            key="summary_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.summary.should_have
                    ]
                )

        if filters.description:
            if filters.description.must_have:
                soft_skills_must.extend(
                    [
                        models.FieldCondition(
                            key="description_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.description.must_have
                    ]
                )

            if filters.description.must_not_have:
                soft_skills_must_not.extend(
                    [
                        models.FieldCondition(
                            key="description_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.description.must_not_have
                    ]
                )

        # 3 Демографические фильтры
        if filters.demographics:
            if filters.demographics.age_range:
                age_range = filters.demographics.age_range
                if age_range.from_value or age_range.to:
                    soft_skills_must.append(
                        models.FieldCondition(
                            key="age",
                            range=models.Range(
                                gte=age_range.from_value, lte=age_range.to
                            ),
                        )
                    )

            if filters.demographics.locations:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="location",
                        match=models.MatchAny(any=filters.demographics.locations),
                    )
                )

        # 4 Опыт работы
        if filters.experience:
            exp = filters.experience
            if exp.min_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_from",
                        range=models.Range(gte=exp.min_years),
                    )
                )
            if exp.max_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_to",
                        range=models.Range(lte=exp.max_years),
                    )
                )

        # 5 Зарплата
        if filters.salary:
            salary = filters.salary
            if salary.min_salary:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="salary_from",
                        range=models.Range(
                            gte=salary.min_salary,
                        ),
                    )
                )

        # 6 Тип занятости
        if filters.employment and filters.employment.types:
            soft_skills_must.append(
                models.FieldCondition(
                    key="employment_type_norm",
                    match=models.MatchAny(any=filters.employment.types),
                )
            )

        filter_hard = {}
        filter_soft = {}

        if hard_skills_must:
            filter_hard["must"] = hard_skills_must
        if hard_skills_should:
            filter_hard["should"] = hard_skills_should
            filter_hard["min_should"] = 1  # type: ignore[assignment]
        if hard_skills_must_not:
            filter_hard["must_not"] = hard_skills_must_not

        if soft_skills_must:
            filter_soft["must"] = soft_skills_must
        if soft_skills_should:
            filter_soft["should"] = soft_skills_should
            # Минимум одно should-условие должно выполниться
            filter_soft["min_should"] = 1  # type: ignore[assignment]
        if soft_skills_must_not:
            filter_soft["must_not"] = soft_skills_must_not

        soft_filter = Filter(**filter_soft) if filter_soft else None
        hard_filter = Filter(**filter_hard) if filter_hard else None

        return soft_filter, hard_filter, soft_vector, hard_vector

    async def filter_search(
        self,
        search_request: SearchRequest,
    ) -> list[T]:
        """Поиск соответствующих работодателей/кандидатов"""

        # проверим какую коллекцию ищем
        match self.entity_cls:
            case cls if cls is CandidateMatch:
                target_collection = QdrantCollection.CANDIDATES.value
            case cls if cls is EmployerMatch:
                target_collection = QdrantCollection.EMPLOYERS.value
            case _:
                raise SearchError("filter_search: Entity not found")

        (
            soft_filter,
            hard_filter,
            soft_vector,
            hard_vector,
        ) = await self._build_qdrant_filters(search_request)

        return await self._filter_search_entities(
            target_collection=target_collection,
            soft_vector=soft_vector,
            hard_vector=hard_vector,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
        )
