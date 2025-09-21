
from numpy import ndarray
from qdrant_client import QdrantClient
from qdrant_client.grpc import VectorParams, Distance, PointStruct

from torch import Tensor



CONFIG = {
    "qdrant_url": "http://localhost:6333",
    "services_collection": "services",
    "masters_collection": "masters",
    "slots_collection": "slots",
}


class QdrantAPI:
    def __init__(self):
        self.client = QdrantClient(url=CONFIG.get("qdrant_url"))

    def create_collection(self, collection_name: str, vectors: int):
        self.client.create_collection(
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
