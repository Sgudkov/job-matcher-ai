from pydantic import BaseModel


class CandidatePayloadBase(BaseModel):
    type: str = ""
    user_id: int = 0
    resume_id: int = 0


class CandidatePayloadSoft(CandidatePayloadBase):
    title: str = ""
    summary: str = ""
    age: int = 0
    location: str = ""
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str = ""
    experience_age: int = 0
    summary_norm: str = ""
    location_norm: str = ""
    employment_type_norm: str = ""
    status: str = "active"


class CandidatePayloadHard(CandidatePayloadBase):
    skill_name: str = ""
    description: str = ""
    experience_age: int = 0
    skill_name_norm: str = ""
    description_norm: str = ""


class EmployerPayloadBase(BaseModel):
    type: str = ""
    employer_id: int = 0
    vacancy_id: int = 0


class EmployerPayloadSoft(EmployerPayloadBase):
    title: str = ""
    summary: str = ""
    experience_age_from: int = 0
    experience_age_to: int = 0
    location: str = ""
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str = ""
    description_norm: str = ""
    location_norm: str = ""
    employment_type_norm: str = ""
    work_mode: str = ""


class EmployerPayloadHard(EmployerPayloadBase):
    skill_name: str = ""
    description: str = ""
    experience_age: int = 0
    skill_name_norm: str = ""
    description_norm: str = ""
