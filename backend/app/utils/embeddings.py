import uuid

from numpy import ndarray
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

from backend.app import config
from backend.app.config import MembersDataType
import numpy as np

from backend.app.models.candidate import CandidateVector
from backend.app.models.embeddings import (
    CandidatePayloadSoft,
    CandidatePayloadHard,
    EmployerPayloadSoft,
    EmployerPayloadHard,
)
from backend.app.models.employer import EmployerVector


class MembersEmbeddingSystem:
    def __init__(self):
        self.soft_model = config.SOFT_MODEL
        self.hard_model = config.HARD_MODEL

    def vectorize_candidate_data(self, candidate: CandidateVector) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        for resume in candidate.resumes:
            embedding_soft = MembersEmbeddingSystem.encode_long_text(
                resume.summary, self.soft_model
            )

            payload = CandidatePayloadSoft(
                type=MembersDataType.SOFT_SKILL.value,
                user_id=candidate.id,
                resume_id=resume.id,
                summary=resume.summary,
                age=candidate.age,
                location=resume.location,
                salary_from=resume.salary_from,
                salary_to=resume.salary_to,
                employment_type=resume.employment_type,
                experience_age=resume.experience_age,
                status=resume.status,
                summary_norm=resume.summary.lower().strip(),
                location_norm=resume.location.lower().strip(),
                employment_type_norm=resume.employment_type.lower().strip(),
            )

            point_struct.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        MembersDataType.SOFT_SKILL.value: embedding_soft.tolist(),
                    },
                    payload=payload.dict(),
                )
            )
            skills = [x for x in candidate.skills if x.resume_id == resume.id]
            for skill in skills:
                embedding_hard = MembersEmbeddingSystem.encode_long_text(
                    skill.skill_name, self.hard_model
                )

                payload = CandidatePayloadHard(
                    type=MembersDataType.HARD_SKILL.value,
                    user_id=candidate.id,
                    resume_id=resume.id,
                    skill_name=skill.skill_name,
                    description=skill.description,
                    skill_name_norm=skill.skill_name.lower().strip(),
                    description_norm=skill.description.lower().strip(),
                )

                point_struct.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector={
                            MembersDataType.HARD_SKILL.value: embedding_hard.tolist(),
                        },
                        payload=payload.dict(),
                    )
                )

        return point_struct

    def vectorize_employer_data(self, employer: EmployerVector) -> list[PointStruct]:
        point_struct: list[PointStruct] = []

        for vacancy in employer.vacancies:
            embedding_soft = MembersEmbeddingSystem.encode_long_text(
                vacancy.description, self.soft_model
            )

            payload = EmployerPayloadSoft(
                type=MembersDataType.SOFT_SKILL.value,
                employer_id=employer.id,
                vacancy_id=vacancy.id,
                summary=vacancy.summary,
                experience_age_from=vacancy.experience_age_from,
                experience_age_to=vacancy.experience_age_to,
                location=vacancy.location,
                salary_from=vacancy.salary_from,
                salary_to=vacancy.salary_to,
                employment_type=vacancy.employment_type,
                work_mode=vacancy.work_mode,
                description_norm=vacancy.description.lower().strip(),
                location_norm=vacancy.location.lower().strip(),
                employment_type_norm=vacancy.employment_type.lower().strip(),
            )

            point_struct.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        MembersDataType.SOFT_SKILL.value: embedding_soft.tolist(),
                    },
                    payload=payload.dict(),
                )
            )
            skills = [x for x in employer.skills if x.vacancy_id == vacancy.id]
            for skill in skills:
                embedding_hard = MembersEmbeddingSystem.encode_long_text(
                    skill.skill_name, self.hard_model
                )

                payload = EmployerPayloadHard(
                    type=MembersDataType.HARD_SKILL.value,
                    employer_id=employer.id,
                    vacancy_id=vacancy.id,
                    skill_name=skill.skill_name,
                    description=skill.description,
                    skill_name_norm=skill.skill_name.lower().strip(),
                    description_norm=skill.description.lower().strip(),
                )

                point_struct.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector={
                            MembersDataType.HARD_SKILL.value: embedding_hard.tolist(),
                        },
                        payload=payload.dict(),
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
