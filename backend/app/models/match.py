from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


@dataclass
class CandidateMatchBase:
    id: UUID = UUID(int=0)
    type: str = ""
    user_id: int = 0
    resume_id: int = 0
    score: float = 0
    summary: str = ""
    age: int = 0
    skill_name: str = ""
    description: str = ""
    location: str = ""
    salary_from: float = 0
    salary_to: float = 0
    employment_type: str = ""
    experience_age: int = 0


@dataclass
class EmployerMatchBase:
    id: UUID = UUID(int=0)
    type: str = ""
    employer_id: int = 0
    vacancy_id: int = 0
    description: str = ""
    skill_name: str = ""
    score: float = 0
    experience_age: int = 0
    location: str = ""
    salary_from: float = 0
    salary_to: float = 0
    employment_type: str = ""


class MatchCreate(BaseModel):
    resume_id: int = 0
    vacancy_id: int = 0
    score: float = 0
    is_new: bool = False


class MatchSearchFilter(BaseModel):
    must_have: list[str] = []
    should_have: list[str] = []
    must_not_have: list[str] = []


class MatchSearchVacancies(BaseModel):
    vacancy_id: int
    hard_search: MatchSearchFilter = MatchSearchFilter()
    soft_search: MatchSearchFilter = MatchSearchFilter()


class MatchVacanciesResponse(BaseModel):
    type: str = ""
    employer_id: int = 0
    vacancy_id: int = 0
    description: str = ""
    skill_name: str = ""
    score: float = 0
    experience_age: int = 0
    location: str = ""
    salary: float = 0
    employment_type: str = ""


class MatchResumesResponse(BaseModel):
    user_id: int = 0
    resume_id: int = 0
    summary: str = ""
    age: int = 0
    skill_name: str = ""
    description: str = ""
    location: str = ""
    salary: float = 0
    employment_type: str = ""
    experience_age: int = 0
