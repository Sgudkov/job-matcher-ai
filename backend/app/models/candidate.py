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
    experience_age: int = 0
    location: str = ""
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str = ""


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


class CandidateUpdate(CandidateCreate):
    id: int


class ResumeCreate(BaseModel):
    candidate_id: int = 0
    title: str = ""
    summary: str = ""
    experience_age: int = 0
    location: str = ""
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str = ""


class CandidateResumeUpsert(ResumeBase):
    pass
