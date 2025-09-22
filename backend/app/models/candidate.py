from dataclasses import field
from typing import List
from uuid import uuid4, UUID

from pydantic import BaseModel
from qdrant_client.models import PointStruct


class CandidateBase(BaseModel):
    id: int = 0
    user_id: UUID = field(default_factory=uuid4)
    first_name: str
    last_name: str
    email: str
    phone: int
    hard_skill: str
    soft_skill: str


class CandidateEmbedding(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class CandidateCreate(CandidateBase):
    pass


# class CandidateMatch(BaseModel):


class CandidateResponse(CandidateBase):
    id: int
    embedding_hard: List[float]
    embedding_soft: List[float]

    class Config:
        from_attributes = True
