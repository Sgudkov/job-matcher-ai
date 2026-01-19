from typing import TypeVar, Type

from numpy import ndarray
from qdrant_client.http.models import Filter, models
from app import config
from app.config import MembersDataType
from app.db.infrastructure.database import QdrantAPI
from app.models.filter import SearchRequest
from app.models.match import (
    EmployerMatch,
    CandidateMatch,
)
from app.utils.embeddings import MembersEmbeddingSystem
from app.utils.filter.collection_resolver import CollectionResolver
from app.utils.filter.filter_builder import QdrantFilterBuilder
from app.utils.filter.score import FilterScore

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
        similarity_threshold: float = 0.4,
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
            query_filter=soft_filter,
        )
        # Будем очищать score, если нет поисковых запросов
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
        key_seed: set[int] = set()
        keys_must = []

        key_name = await self.entity_cls().get_key_name_value()
        key_name = key_name[0]

        # Соберем ключи и score в одно место
        for com in complex_result.points:
            keys = await self.entity_cls(**com.payload).get_key_name_value()
            complex_scores.setdefault(keys, []).append(com.score)
            key_seed.add(keys[1])
        else:
            keys_must.append(
                models.FieldCondition(
                    key=key_name, match=models.MatchAny(any=list(key_seed))
                )
            )
        # Получаем среднее score по ключу,
        # соберем фильтр
        averaged_scores: dict[int, float] = {}
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

        score_util = FilterScore(
            points=result_points[0],
            hard_filter=hard_filter,
            soft_filter=soft_filter,
            hard_vector_not=hard_vector_not,
            soft_vector_not=soft_vector_not,
            entity_cls=self.entity_cls,
            averaged_scores=averaged_scores,
            similarity_threshold=similarity_threshold,
        )

        await score_util.calc_score()

        return score_util.assemble_results(clear_score)

    async def filter_search(
        self,
        search_request: SearchRequest,
    ) -> list[T]:
        """Поиск соответствующих работодателей/кандидатов"""

        target_collection = CollectionResolver.resolve(self.entity_cls)

        filter_builder = QdrantFilterBuilder(
            config=config, embedding_system=MembersEmbeddingSystem()
        )
        (
            soft_filter,
            hard_filter,
            soft_vector,
            hard_vector,
            hard_vector_not,
            soft_vector_not,
        ) = await filter_builder.build(search_request)

        return await self._filter_search_entities(
            target_collection=target_collection,
            hard_vector_not=hard_vector_not,
            soft_vector_not=soft_vector_not,
            soft_vector=soft_vector,
            hard_vector=hard_vector,
            soft_filter=soft_filter,
            hard_filter=hard_filter,
        )
