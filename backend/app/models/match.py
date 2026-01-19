from pydantic import BaseModel

from app.models.embeddings import (
    CandidatePayloadSoft,
    CandidatePayloadHard,
    EmployerPayloadSoft,
    EmployerPayloadHard,
)


# ============================================================================
# ВНУТРЕННИЕ МОДЕЛИ ДЛЯ РАБОТЫ С ВЕКТОРАМИ (используются в filter.py)
# ============================================================================


class CandidateMatch(CandidatePayloadSoft, CandidatePayloadHard):
    """Внутренняя модель для агрегации векторов кандидата"""

    id: str = ""
    score: float = 0

    async def get_complex_key(self):
        return f"{self.user_id}_{self.resume_id}"

    async def get_key_name_value(self):
        return "resume_id", self.resume_id


class EmployerMatch(EmployerPayloadSoft, EmployerPayloadHard):
    """Внутренняя модель для агрегации векторов работодателя"""

    id: str = ""
    score: float = 0

    async def get_complex_key(self):
        return f"{self.employer_id}_{self.vacancy_id}"

    async def get_key_name_value(self):
        return "vacancy_id", self.vacancy_id


# ============================================================================
# МОДЕЛИ ОТВЕТА ДЛЯ API (используются в routes)
# ============================================================================


class SkillMatch(BaseModel):
    """Навык с описанием"""

    skill_name: str
    description: str = ""
    experience_age: int = 0


class ResumeMatchResponse(BaseModel):
    """Ответ с данными резюме для отображения"""

    # Идентификаторы
    user_id: int
    resume_id: int

    # Основная информация (из soft-вектора)
    title: str  # Короткое название резюме
    summary: str  # Полное описание
    age: int = 0
    location: str
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str
    experience_age: int = 0
    status: str = "active"

    # Навыки (агрегированные из hard-векторов)
    skills: list[SkillMatch] = []

    # Метрика совпадения
    score: float = 0.0


class VacancyMatchResponse(BaseModel):
    """Ответ с данными вакансии для отображения"""

    # Идентификаторы
    employer_id: int
    vacancy_id: int

    # Основная информация (из soft-вектора)
    title: str  # Короткое название вакансии
    summary: str  # Полное описание
    experience_age_from: int = 0
    experience_age_to: int = 0
    location: str
    salary_from: int = 0
    salary_to: int = 0
    employment_type: str
    work_mode: str = ""

    # Навыки (агрегированные из hard-векторов)
    skills: list[SkillMatch] = []

    # Метрика совпадения
    score: float = 0.0


# ============================================================================
# МОДЕЛИ ДЛЯ БД
# ============================================================================


class MatchCreate(BaseModel):
    resume_id: int = 0
    vacancy_id: int = 0
    score: float = 0
    is_new: bool = False
