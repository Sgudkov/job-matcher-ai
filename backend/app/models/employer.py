from dataclasses import field
from uuid import UUID, uuid4

from pydantic import BaseModel
from qdrant_client.http.models import PointStruct


class EmployerBase(BaseModel):
    id: int = 0
    employer_id: UUID = field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
    phone: int
    hard_skill: str
    soft_skill: str


class EmployerEmbedding(BaseModel):
    embedding_soft: list[PointStruct] = field(default_factory=list)
    embedding_hard: list[PointStruct] = field(default_factory=list)


class EmployerCreate(EmployerBase):
    pass


class EmployerResponse(EmployerBase):
    id: int
    embedding_hard: list[float]
    embedding_soft: list[float]

    class Config:
        from_attributes = True
