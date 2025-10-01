# Настройки (API ключи, переменные окружения)
from enum import Enum

from pydantic_settings import BaseSettings
from sentence_transformers import SentenceTransformer


class QdrantCollection(Enum):
    CANDIDATES = "candidates"
    EMPLOYERS = "employers"


class MembersDataType(Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    SKILL_NAME = "skill_name_norm"
    DESCRIPTION = "description_norm"
    SUMMARY = "summary_norm"


SOFT_MODEL = SentenceTransformer("ai-forever/ru-en-RoSBERTa")
HARD_MODEL = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")


class Settings(BaseSettings):
    PROJECT_NAME: str = "job-matcher"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
