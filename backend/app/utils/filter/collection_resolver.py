from typing import Type, TypeVar

from app.config import QdrantCollection
from app.models.match import CandidateMatch, EmployerMatch

T = TypeVar("T", EmployerMatch, CandidateMatch)


class SearchError(Exception):
    """Ошибка при поиске совпадений."""

    pass


class CollectionResolver:
    @staticmethod
    def resolve(entity_cls: Type[T]) -> str:
        if entity_cls is CandidateMatch:
            return QdrantCollection.CANDIDATES.value
        if entity_cls is EmployerMatch:
            return QdrantCollection.EMPLOYERS.value
        raise SearchError("Entity not found")
