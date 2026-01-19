import logging
import os
from typing import Any

from dotenv import load_dotenv
from numpy import ndarray
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    PointStruct,
    Record,
    models,
    Filter,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sympy.tensor.tensor import Tensor


from app.config import MembersDataType, QdrantCollection

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL")

# Асинхронное engine
engine = create_async_engine(
    str(DATABASE_URL),
    echo=True,  # Логирование SQL запросов
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
)

# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency для получения сессии
async def get_db():
    """Получение сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session


class QdrantAPI:
    def __init__(self):
        try:
            self.client = QdrantClient(url=QDRANT_URL)

            logger.info("Подключение к Qdrant успешно")
        except Exception as e:
            logger.error(f"Ошибка подключения к Qdrant: {e}")
            raise ValueError(e)

    def create_collection(self, collection_name: str) -> bool:
        """Создание коллекции"""
        return self.client.create_collection(
            collection_name=collection_name,
            vectors_config={
                MembersDataType.HARD_SKILL.value: VectorParams(
                    size=384, distance=Distance.COSINE
                ),
                MembersDataType.SOFT_SKILL.value: VectorParams(
                    size=1024, distance=Distance.COSINE
                ),
            },
        )

    def add_vectors(self, collection_name: str, vectors: list[PointStruct]):
        """Добавить вектор в БД"""
        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=vectors,
        )

    def search(
        self,
        collection_name: str,
        vector: Tensor | ndarray | dict[str, Tensor],
        limit: int,
        **kwargs,
    ):
        """Поиск вектора в БД"""
        must = []
        args = kwargs.get("kwargs", {})
        for key, value in args.items():
            must.append(
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
            )
        return self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
            query_filter=Filter(must=must),
        )

    def scroll(
        self, collection_name: str, limit: int, **kwargs
    ) -> tuple[list[Record], int | str | None | Any]:
        """Скролл по коллекции"""
        must: list = []
        for key, value in kwargs.items():
            must.append(
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
            )

        return self.client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(must=must),
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )

    def retrieve(
        self, collection_name: str, member_uuid: list[int | str]
    ) -> list[Record]:
        """Получить записи по uuid"""
        return self.client.retrieve(
            collection_name=collection_name, ids=member_uuid, with_vectors=True
        )

    async def remove_employer_skills(self, employer_id: int, vacancy_id: int):
        """Удаление навыков работодателя"""
        keys = {
            "type": MembersDataType.SOFT_SKILL.value,
            "employer_id": employer_id,
            "vacancy_id": vacancy_id,
        }

        self._remove_points(
            collection_name=QdrantCollection.EMPLOYERS.value, kwargs=keys
        )

        keys["type"] = MembersDataType.HARD_SKILL.value
        self._remove_points(
            collection_name=QdrantCollection.EMPLOYERS.value, kwargs=keys
        )

    async def remove_candidate_skills(self, candidate_id: int, resume_id: int):
        """Удаление навыков кандидата"""
        keys = {
            "type": MembersDataType.SOFT_SKILL.value,
            "user_id": candidate_id,
            "resume_id": resume_id,
        }

        self._remove_points(
            collection_name=QdrantCollection.CANDIDATES.value, kwargs=keys
        )

        keys["type"] = MembersDataType.HARD_SKILL.value
        self._remove_points(
            collection_name=QdrantCollection.CANDIDATES.value, kwargs=keys
        )

    def _remove_points(self, collection_name: str, **kwargs):
        """Удаление записей по условию"""
        must = []
        args = kwargs.get("kwargs", {})
        for key, value in args.items():
            must.append(
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
            )
        self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(filter=models.Filter(must=must)),
        )


qdrant_api = QdrantAPI()
