# Настройки (API ключи, переменные окружения)
from enum import Enum

from pydantic_settings import BaseSettings


class QdrantCollection(Enum):
    CANDIDATES_HARD = "candidates_hard"
    CANDIDATES_SOFT = "candidates_soft"
    EMPLOYERS_HARD = "employers_hard"
    EMPLOYERS_SOFT = "employers_soft"


class MembersDataType(Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"


class Settings(BaseSettings):
    PROJECT_NAME: str = "job-matcher"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
