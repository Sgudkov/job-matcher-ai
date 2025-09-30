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

    async def get_complex_key(self):
        return f"{self.user_id}_{self.resume_id}"

    async def get_key_name_value(self):
        return "resume_id", self.resume_id


class EmployerMatch(EmployerPayloadSoft, EmployerPayloadHard):
    id: str = ""
    score: float = 0

    async def get_complex_key(self):
        return f"{self.employer_id}_{self.vacancy_id}"

    async def get_key_name_value(self):
        return "vacancy_id", self.vacancy_id


class MatchCreate(BaseModel):
    resume_id: int = 0
    vacancy_id: int = 0
    score: float = 0
    is_new: bool = False
