import logging
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Асинхронное engine
engine = create_async_engine(
    str(DATABASE_URL),
    echo=True,  # Логирование SQL запросов
    future=True,
    pool_size=20,
    max_overflow=0
)

# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
