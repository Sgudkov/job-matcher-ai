from pydantic import BaseModel

from backend.app.models.embeddings import (
    CandidatePayloadSoft,
    CandidatePayloadHard,
    EmployerPayloadSoft,
    EmployerPayloadHard,
)


class CandidateMatch(CandidatePayloadSoft, CandidatePayloadHard):
    id: str = ""
    score: float = 0


class EmployerMatch(EmployerPayloadSoft, EmployerPayloadHard):
    id: str = ""
    score: float = 0


class MatchCreate(BaseModel):
    resume_id: int = 0
    vacancy_id: int = 0
    score: float = 0
    is_new: bool = False
