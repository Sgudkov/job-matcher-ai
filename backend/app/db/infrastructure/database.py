import logging
import os

from dotenv import load_dotenv
from numpy import ndarray
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, Record
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from torch import Tensor

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
    max_overflow=0
)

# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class QdrantAPI:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)

    def create_collection(self, collection_name: str, vectors: int) -> bool:
        return self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vectors, distance=Distance.COSINE),
        )

    def add_vectors(self, collection_name: str, vectors: list[PointStruct]):
        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=vectors,
        )

    def search(self, collection_name: str, vector: Tensor | ndarray | dict[str, Tensor], limit: int):
        return self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )

    def retrieve(self, collection_name: str, member_uuid: list[int | str]) -> list[Record]:
        return self.client.retrieve(
            collection_name=collection_name,
            ids=member_uuid,
            with_vectors=True
        )


qdrant_api = QdrantAPI()
