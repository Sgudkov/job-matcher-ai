
from numpy import ndarray
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from backend.app.config import MembersDataType
import numpy as np

from backend.app.models.candidate import CandidateBase
from backend.app.models.employer import EmployerBase


class MembersEmbeddingSystem:
    def __init__(self):
        self.soft_model = SentenceTransformer("ai-forever/ru-en-RoSBERTa")
        self.hard_model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

    def vectorize_candidate_data(self, candidate: CandidateBase, skill: MembersDataType) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        candidate_data: str = ""

        match skill:
            case MembersDataType.SOFT_SKILL:
                model = self.soft_model
                candidate_data = candidate.soft_skill
            case MembersDataType.HARD_SKILL:
                model = self.hard_model
                candidate_data = candidate.hard_skill
            case _:
                model = self.soft_model

        embedding = MembersEmbeddingSystem.encode_long_text(candidate_data, model)

        point_struct.append(
            PointStruct(
                id=str(candidate.user_id),
                vector=embedding.tolist(),
            ))

        return point_struct

    def vectorize_employer_data(self, employer: EmployerBase, skill: MembersDataType) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        employer_data: str = ""

        match skill:
            case MembersDataType.SOFT_SKILL:
                model = self.soft_model
                employer_data = employer.soft_skill
            case MembersDataType.HARD_SKILL:
                model = self.hard_model
                employer_data = employer.hard_skill
            case _:
                model = self.soft_model

        embedding = MembersEmbeddingSystem.encode_long_text(employer_data, model)

        point_struct.append(
            PointStruct(
                id=str(employer.employer_id),
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


members_embedding_system = MembersEmbeddingSystem()
