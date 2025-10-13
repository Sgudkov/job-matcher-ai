# Настройки (API ключи, переменные окружения)
from enum import Enum

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from sentence_transformers import SentenceTransformer

# Загрузка переменных окружения
load_dotenv()


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
    """Настройки приложения из переменных окружения"""

    PROJECT_NAME: str = "job-matcher"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = ""
    DATABASE_SYNC_URL: str = ""

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"

    # Auth
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 30.0

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Игнорировать дополнительные поля из .env
    )


settings = Settings()
