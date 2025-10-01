from dataclasses import field
from datetime import datetime
from typing import List

from pydantic import BaseModel
from qdrant_client.models import PointStruct


class ResumeSkillBase(BaseModel):
    resume_id: int = 0
    skill_name: str = ""
    description: str = ""


class ResumeData(BaseModel):
    candidate_id: int = 0
    title: str = ""
    summary: str = ""
    experience_age: int = 0
    location: str = ""
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str = ""
    status: str = "active"


class ResumeBase(ResumeData):
    id: int = 0


class CandidateBase(BaseModel):
    id: int = 0
    first_name: str
    last_name: str
    age: int
    email: str
    phone: int

    class Config:
        from_attributes = True


class CandidateVector(CandidateBase):
    resumes: List[ResumeBase] = field(default_factory=list)
    skills: List[ResumeSkillBase] = field(default_factory=list)


class CandidateEmbedding(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    email: str
    phone: int


class CandidateUpdate(CandidateCreate):
    id: int


class ResumeCreate(ResumeData):
    id: int | None = None
    created_at: datetime | None = field(default_factory=datetime.now)
    updated_at: datetime | None = field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ResumeUpsert(ResumeBase):
    pass
