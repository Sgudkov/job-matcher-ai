from dataclasses import field
from typing import List

from pydantic import BaseModel
from qdrant_client.models import PointStruct


class ResumeSkill(BaseModel):
    resume_id: int = 0
    skill_name: str = ""
    description: str = ""


class ResumeBase(BaseModel):
    id: int = 0
    candidate_id: int = 0
    title: str = ""
    summary: str = ""


class CandidateBase(BaseModel):
    id: int = 0
    first_name: str
    last_name: str
    age: int
    email: str
    phone: int


class CandidateVector(CandidateBase):
    resumes: List[ResumeBase] = field(default_factory=list)
    skills: List[ResumeSkill] = field(default_factory=list)


class CandidateEmbedding(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: str
    phone: int


class CandidateResumeUpsert(ResumeBase):
    pass


class CandidateResponse(CandidateBase):
    id: int
    embedding_hard: List[float]
    embedding_soft: List[float]

    class Config:
        from_attributes = True
