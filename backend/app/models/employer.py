from dataclasses import field

from pydantic import BaseModel
from qdrant_client.http.models import PointStruct


class VacancySkill(BaseModel):
    vacancy_id: int = 0
    skill_name: str = ""
    description: str = ""


class VacancyBase(BaseModel):
    id: int = 0
    employer_id: int = 0
    title: str = ""
    description: str = ""


class EmployerBase(BaseModel):
    id: int = 0
    first_name: str
    last_name: str
    email: str
    phone: int


class EmployerEmbedding(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class EmployerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: int


class EmployerVacancyUpsert(VacancyBase):
    pass


class EmployerVector(EmployerBase):
    vacancies: list[VacancyBase] = field(default_factory=list)
    skills: list[VacancySkill] = field(default_factory=list)


class EmployerResponse(EmployerBase):
    id: int
    embedding_hard: list[float]
    embedding_soft: list[float]

    class Config:
        from_attributes = True
