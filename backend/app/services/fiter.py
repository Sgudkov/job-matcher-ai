from typing import TypeVar, Type, Tuple

from numpy import ndarray
from qdrant_client.http.models import Filter, models

from backend.app import config
from backend.app.config import MembersDataType, QdrantCollection
from backend.app.db.infrastructure.database import QdrantAPI
from backend.app.models.filter import SearchRequest, SearchFilters
from backend.app.models.match import (
    EmployerMatch,
    CandidateMatch,
    ResumeMatchResponse,
    VacancyMatchResponse,
    SkillMatch,
)
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
        hard_vector_not: ndarray | None = None,
        soft_vector_not: ndarray | None = None,
        soft_vector: ndarray | None = None,
        hard_vector: ndarray | None = None,
        soft_filter: Filter | None = None,
        hard_filter: Filter | None = None,
        similarity_threshold: float = 0.6,
        top_k: int = 20,
        alpha: float = 0.8,
    ) -> list[T]:
        """Ищем данные по векторам и фильтрам"""

        # Получаем все записи удовлетворяющие фильтрам
        complex_result = self.qdrant_api.client.query_points(
            collection_name=target_collection,
            query=models.FusionQuery(fusion=models.Fusion.DBSF),
            prefetch=[
                models.Prefetch(
                    query=hard_vector,
                    using=MembersDataType.HARD_SKILL.value,
                    filter=hard_filter,
                    limit=100,
                ),
                models.Prefetch(
                    query=soft_vector,
                    using=MembersDataType.SOFT_SKILL.value,
                    filter=soft_filter,
                    limit=100,
                ),
            ],
            limit=100,
            with_vectors=True,
        )
        clear_score = (
            True
            if (
                hard_vector is None
                and hard_filter is None
                and soft_vector is None
                and soft_filter is None
            )
            else False
        )
        complex_scores: dict[set, list] = {}
        key_seed = set()
        keys_must = []
        decrease_score = set()
        increase_score: dict[int, float] = {}

        # Соберем ключи и score в одно место
        for com in complex_result.points:
            keys = await self.entity_cls(**com.payload).get_key_name_value()
            complex_scores.setdefault(keys, []).append(com.score)
            key_seed.add(keys[1])
        else:
            keys_must.append(
                models.FieldCondition(
                    key=keys[0], match=models.MatchAny(any=list(key_seed))
                )
            )
        # Получаем среднее score по ключу,
        # соберем фильтр
        averaged_scores: dict[int, int] = {}
        for item_id, scores in complex_scores.items():
            item_id_list = list(item_id)
            averaged_scores[item_id_list[1]] = sum(scores) / len(scores)

        result_filter = Filter(must=keys_must or None)

        result_points = self.qdrant_api.client.scroll(
            collection_name=target_collection,
            scroll_filter=result_filter,
            with_payload=True,
            with_vectors=True,
            limit=100,
        )
        result_scores: dict[int, float] = {}
        hards: dict[int, list] = {}
        softs: dict = {}

        # Соберем результат в {ключ,score} -> payload
        for res in result_points[0]:
            keys = await self.entity_cls(**res.payload).get_key_name_value()
            if res.payload.get("type", "") == "soft_skill":
                softs[keys[1]] = res.payload
            elif res.payload.get("type", "") == "hard_skill":
                hards.setdefault(keys[1], []).append(res.payload)

                # Сравним вектора, если > similarity_threshold запомним для штрафа
                curr_vector = res.vector.get(MembersDataType.HARD_SKILL.value, [])

                if hard_vector_not and curr_vector:
                    print(keys[1])
                    print(self._cosine_similarity(hard_vector_not, curr_vector))

                skill_name = res.payload.get("skill_name_norm", "")

                if hard_filter:
                    if hard_filter.must_not:
                        if any(
                            must_not.match.text in skill_name
                            for must_not in hard_filter.must_not
                        ):
                            # Если хотя бы одна строка из must_not содержится в skill_name, выполните действия
                            decrease_score.add(keys[1])
                    if hard_filter.must:
                        if any(
                            must.match.text in skill_name for must in hard_filter.must
                        ):
                            # За каждое упоминание добавляем 0,1 к score
                            increase_score.setdefault(keys[1], 0.1)
                            increase_score[keys[1]] += 0.1

                if (hard_vector_not and curr_vector) and self._cosine_similarity(
                    hard_vector_not, curr_vector
                ) > similarity_threshold:
                    decrease_score.add(keys[1])

                if (soft_vector_not and curr_vector) and self._cosine_similarity(
                    soft_vector_not, curr_vector
                ) > similarity_threshold:
                    decrease_score.add(keys[1])

            result_scores[keys[1]] = averaged_scores.get(keys[1], 0)

        result = []

        for s_key, soft in softs.items():
            skills: list[SkillMatch] = []
            for k, v in hards.items():
                if k == s_key:
                    skills.extend([SkillMatch(**skill2) for skill2 in v])

            score = result_scores.get(s_key, 0)

            score = 0 if clear_score else score

            # Если ключ попался в исключении, понижаем score
            if s_key in decrease_score:
                score *= 0.5

            # Если ключ в поиске, увеличиваем score
            score += increase_score.setdefault(s_key, 0)

            if self.entity_cls is CandidateMatch:
                result.append(
                    ResumeMatchResponse(
                        user_id=soft.get("user_id", ""),
                        resume_id=soft.get("resume_id", ""),
                        title=soft.get("title", ""),
                        summary=soft.get("summary", ""),
                        age=soft.get("age", ""),
                        location=soft.get("location", ""),
                        salary_from=soft.get("salary_from", ""),
                        salary_to=soft.get("salary_to", ""),
                        employment_type=soft.get("employment_type", ""),
                        experience_age=soft.get("experience_age", ""),
                        status=soft.get("status", ""),
                        skills=skills,
                        score=score,
                    )
                )
            elif self.entity_cls is EmployerMatch:
                result.append(
                    VacancyMatchResponse(
                        employer_id=soft.get("employer_id", ""),
                        vacancy_id=soft.get("vacancy_id", ""),
                        title=soft.get("title", ""),
                        summary=soft.get("summary", ""),
                        experience_age_from=soft.get("experience_age_from", ""),
                        experience_age_to=soft.get("experience_age_to", ""),
                        location=soft.get("location", ""),
                        salary_from=soft.get("salary_from", ""),
                        salary_to=soft.get("salary_to", ""),
                        employment_type=soft.get("employment_type", ""),
                        work_mode=soft.get("work_mode", ""),
                        skills=skills,
                        score=score,
                    )
                )
        return result

    async def _load_all_vectors_for_entities(
        self,
        target_collection: str,
        entity_keys: set[str],
    ) -> list[T]:
        """
        Загружает ВСЕ векторы (soft + hard) для найденных резюме/вакансий.

        Args:
            target_collection: коллекция Qdrant
            entity_keys: множество ключей вида "user_id_resume_id" или "employer_id_vacancy_id"

        Returns:
            Список всех векторов для этих сущностей
        """
        all_vectors = []

        for entity_key in entity_keys:
            # Парсим ключ в зависимости от типа сущности
            if self.entity_cls is CandidateMatch:
                # Формат: "user_id_resume_id"
                parts = entity_key.split("_")
                if len(parts) >= 2:
                    resume_id = int(parts[-1])

                    # Загружаем все векторы этого резюме
                    result, _ = self.qdrant_api.client.scroll(
                        collection_name=target_collection,
                        scroll_filter=Filter(
                            must=[
                                models.FieldCondition(
                                    key="resume_id",
                                    match=models.MatchValue(value=resume_id),
                                )
                            ]
                        ),
                        limit=100,
                        with_vectors=False,
                        with_payload=True,
                    )

                    for point in result:
                        # Создаем объект и генерируем уникальный ключ из payload
                        vector = self.entity_cls(**point.payload)  # type: ignore[call-arg]
                        vector.id = await vector.get_complex_key()
                        all_vectors.append(vector)

            elif self.entity_cls is EmployerMatch:
                # Формат: "employer_id_vacancy_id"
                parts = entity_key.split("_")
                if len(parts) >= 2:
                    vacancy_id = int(parts[-1])

                    # Загружаем все векторы этой вакансии
                    result, _ = self.qdrant_api.client.scroll(
                        collection_name=target_collection,
                        scroll_filter=Filter(
                            must=[
                                models.FieldCondition(
                                    key="vacancy_id",
                                    match=models.MatchValue(value=vacancy_id),
                                )
                            ]
                        ),
                        limit=100,
                        with_vectors=False,
                        with_payload=True,
                    )

                    for point in result:
                        # Создаем объект и генерируем уникальный ключ из payload
                        vector = self.entity_cls(**point.payload)  # type: ignore[call-arg]
                        vector.id = await vector.get_complex_key()
                        all_vectors.append(vector)

        return all_vectors

    async def _is_must_excluded(
        self,
        target_collection: str,
        keys: tuple,
        vector_name: str,
        similarity_threshold: float,
        must_not_vectors: list[list[float]],
    ) -> bool:
        """Проверяем вхождение в must_not"""
        points = self.qdrant_api.client.query_points(
            collection_name=target_collection,
            using=vector_name,
            query_filter=Filter(
                must=[
                    models.FieldCondition(
                        key=keys[0], match=models.MatchValue(value=keys[1])
                    )
                ]
            ),
            limit=50,
            with_vectors=True,  # важно получить векторы!
        )

        for point in points.points:
            point_vector = point.vector.get(vector_name, [])
            if not point_vector:
                continue
            for vector in must_not_vectors:
                if self._cosine_similarity(point_vector, vector) > similarity_threshold:
                    return True

        return False

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Вычисляет косинусную схожесть между векторами."""
        import numpy as np

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def _build_qdrant_filters(
        self, search_request: SearchRequest
    ) -> Tuple[
        Filter | None,
        Filter | None,
        ndarray | None,
        ndarray | None,
        ndarray | None,
        ndarray | None,
    ]:
        soft_skills_must: list[models.FieldCondition] = []
        soft_skills_should: list[models.FieldCondition] = []
        soft_skills_must_not: list[models.FieldCondition] = []

        hard_skills_must: list[models.FieldCondition] = []
        hard_skills_should: list[models.FieldCondition] = []
        hard_skills_must_not: list[models.FieldCondition] = []
        filters: SearchFilters = search_request.filters

        # Векторизуем hard и soft скиллы

        skills_must = filters.skills.must_have if filters.skills else []
        skills_should = filters.skills.should_have if filters.skills else []
        description_must = filters.description.must_have if filters.description else []
        description_should = (
            filters.description.should_have if filters.description else []
        )

        # Векторизуем по требуемым навыкам в вакансии/резюме
        text_hard = " ".join(
            [
                f"{', '.join([s.lower().strip() for s in skills_must])}",
                f"{', '.join([s.lower().strip() for s in skills_should])}",
                f"{', '.join([s.lower().strip() for s in description_must])}",
                f"{', '.join([s.lower().strip() for s in description_should])}",
            ]
        ).strip()

        if text_hard:
            hard_vector = MembersEmbeddingSystem.encode_long_text(
                model=config.HARD_MODEL, text=text_hard
            )
        else:
            hard_vector = None

        summary_must = filters.summary.must_have if filters.summary else []
        summary_should = filters.summary.should_have if filters.summary else []

        # Векторизуем по описанию в вакансии/резюме
        text_soft = " ".join(
            [
                f"{', '.join([s.lower().strip() for s in summary_must])}",
                f"{','.join([s.lower().strip() for s in summary_should])}",
            ]
        ).strip()

        if text_soft:
            soft_vector = MembersEmbeddingSystem.encode_long_text(
                model=config.SOFT_MODEL, text=text_soft
            )
        else:
            soft_vector = None

        # Векторизуем skills must_not_have для исключения в post-обработке
        skills_must_not = filters.skills.must_not_have if filters.skills else []
        hard_vector_not = []
        for skill in skills_must_not:
            vector = MembersEmbeddingSystem.encode_long_text(
                model=config.HARD_MODEL, text=skill.lower()
            )
            hard_vector_not.append(vector)

        if not hard_vector_not:
            hard_vector_not = None  # type: ignore[assignment]

        # Векторизуем summary must_not_have для исключения в post-обработке
        summary_must_not = filters.summary.must_not_have if filters.summary else []
        soft_vector_not = []
        for summary in summary_must_not:
            vector = MembersEmbeddingSystem.encode_long_text(
                model=config.SOFT_MODEL, text=summary.lower()
            )
            soft_vector_not.append(vector)

        if not soft_vector_not:
            soft_vector_not = None  # type: ignore[assignment]

        # Соберем фильтры

        # 1 Hard skills фильтры

        # Дополнительно жестко ограничим навыки, если они пришли в фильтре
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

            # MatchText работает как полнотекстовый поиск
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
        # if filters.summary:

        # if filters.summary.must_not_have:
        #     soft_skills_must_not.extend(
        #         [
        #             models.FieldCondition(
        #                 key="summary_norm",
        #                 match=models.MatchText(text=skill.lower()),
        #             )
        #             for skill in filters.summary.must_not_have
        #         ]
        #     )

        # Добавили в векторизацию
        # if filters.summary.should_have:
        #     soft_skills_should.extend(
        #         [
        #             models.FieldCondition(
        #                 key="summary_norm",
        #                 match=models.MatchText(text=skill.lower()),
        #             )
        #             for skill in filters.summary.should_have
        #         ]
        #     )

        # Исключим из результатов стоп слова
        if filters.description:
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
                                gte=age_range.from_value or None,
                                lte=age_range.to or None,
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

        # 4 Опыт в вакансии
        if filters.experience_vacancy:
            exp = filters.experience_vacancy
            if exp.min_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_from",
                        range=models.Range(gte=exp.min_years or None),
                    )
                )

            if exp.max_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_to",
                        range=models.Range(lte=exp.max_years or None),
                    )
                )

        # 5 Опыт в резюме
        if filters.experience_resume:
            exp = filters.experience_resume
            if exp.min_years or exp.max_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age",
                        range=models.Range(
                            gte=exp.min_years or None, lte=exp.max_years or None
                        ),
                    )
                )

        # 6 Зарплата
        if filters.salary:
            salary = filters.salary
            if salary.min_salary:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="salary_from",
                        range=models.Range(gte=salary.min_salary or None),
                    )
                )
            if salary.max_salary:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="salary_to",
                        range=models.Range(lte=salary.max_salary or None),
                    )
                )

        # 7 Тип занятости
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
            # filter_hard["min_should"] = 1  # type: ignore[assignment]
        if hard_skills_must_not:
            filter_hard["must_not"] = hard_skills_must_not

        if soft_skills_must:
            filter_soft["must"] = soft_skills_must
        if soft_skills_should:
            filter_soft["should"] = soft_skills_should
            # Минимум одно should-условие должно выполниться
            # filter_soft["min_should"] = 1  # type: ignore[assignment]
        if soft_skills_must_not:
            filter_soft["must_not"] = soft_skills_must_not

        soft_filter = Filter(**filter_soft) if filter_soft else None
        hard_filter = Filter(**filter_hard) if filter_hard else None

        return (
            soft_filter,
            hard_filter,
            soft_vector,
            hard_vector,
            hard_vector_not,
            soft_vector_not,
        )

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
            hard_vector_not,
            soft_vector_not,
        ) = await self._build_qdrant_filters(search_request)

        return await self._filter_search_entities(
            target_collection=target_collection,
            hard_vector_not=hard_vector_not,
            soft_vector_not=soft_vector_not,
            soft_vector=soft_vector,
            hard_vector=hard_vector,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
        )
