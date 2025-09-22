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
        self.hard_model = SentenceTransformer(
            "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        )

    def vectorize_candidate_data(self, candidate: CandidateBase) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        embedding_soft = MembersEmbeddingSystem.encode_long_text(
            candidate.soft_skill, self.soft_model
        )
        embedding_hard = MembersEmbeddingSystem.encode_long_text(
            candidate.hard_skill, self.hard_model
        )

        point_struct.append(
            PointStruct(
                id=str(candidate.user_id),
                vector={
                    MembersDataType.SOFT_SKILL.value: embedding_soft.tolist(),
                    MembersDataType.HARD_SKILL.value: embedding_hard.tolist(),
                },
            )
        )

        return point_struct

    def vectorize_employer_data(self, employer: EmployerBase) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        embedding_soft = MembersEmbeddingSystem.encode_long_text(
            employer.soft_skill, self.soft_model
        )
        embedding_hard = MembersEmbeddingSystem.encode_long_text(
            employer.hard_skill, self.hard_model
        )

        point_struct.append(
            PointStruct(
                id=str(employer.employer_id),
                vector={
                    MembersDataType.SOFT_SKILL.value: embedding_soft.tolist(),
                    MembersDataType.HARD_SKILL.value: embedding_hard.tolist(),
                },
            )
        )

        return point_struct

    @staticmethod
    def encode_long_text(
        text, model: SentenceTransformer, chunk_size=512, overlap=50
    ) -> ndarray:
        """
        Векторизация длинного текста с разбиением на chunks
        """
        # Разбиваем текст на предложения или слова
        words = text.split()
        chunks = []

        # Создаем overlapping chunks
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)

        # Кодируем все chunks
        chunk_embeddings = model.encode(chunks)

        # Усредняем embeddings всех chunks
        return np.mean(chunk_embeddings, axis=0)


members_embedding_system = MembersEmbeddingSystem()
