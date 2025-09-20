from uuid import uuid4

from numpy import ndarray
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from backend.app.config import SalonDataType
import numpy as np


class CandidateEmbeddingSystem:
    def __init__(self):
        self.soft_model = SentenceTransformer("ai-forever/ru-en-RoSBERTa")
        self.hard_model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

    def vectorize_candidate_data(self, candidate_data: str, skill: SalonDataType) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        match skill:
            case SalonDataType.SOFT_SKILL:
                model = self.soft_model
            case SalonDataType.HARD_SKILL:
                model = self.hard_model
            case _:
                model = self.soft_model

        embedding = CandidateEmbeddingSystem.encode_long_text(candidate_data, model)

        point_struct.append(
            PointStruct(
                id=int(uuid4()),
                vector=embedding.tolist(),
            ))

        return point_struct

    def vectorize_employer_data(self, employer_data: str, skill: SalonDataType) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        match skill:
            case SalonDataType.SOFT_SKILL:
                model = self.soft_model
            case SalonDataType.HARD_SKILL:
                model = self.hard_model
            case _:
                model = self.soft_model

        embedding = CandidateEmbeddingSystem.encode_long_text(employer_data, model)

        point_struct.append(
            PointStruct(
                id=int(uuid4()),
                vector=embedding.tolist(),
            ))

        return point_struct

    @staticmethod
    def encode_long_text(text, model: SentenceTransformer, chunk_size=512, overlap=50) -> ndarray:
        """
        Векторизация длинного текста с разбиением на chunks
        """
        # Разбиваем текст на предложения или слова
        words = text.split()
        chunks = []

        # Создаем overlapping chunks
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

        # Кодируем все chunks
        chunk_embeddings = model.encode(chunks)

        # Усредняем embeddings всех chunks
        return np.mean(chunk_embeddings, axis=0)


candidate_embedding_system = CandidateEmbeddingSystem()
