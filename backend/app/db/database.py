import asyncio
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_db():
    try:
        async_engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # Логирование SQL запросов
            future=True,
            pool_size=20,
            max_overflow=0
        )

        async with async_engine.begin() as conn:

            result = await conn.execute(text("SELECT version()"))

            logger.info(result.scalars())
            logger.info("База данных подключена")

            # Проверить доступность базы данных
            result = await conn.execute(text("SELECT current_database()"))
            logger.info(f"База данных доступна: {result.scalars()}")

    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")


if __name__ == "__main__":
    asyncio.run(connect_db())
