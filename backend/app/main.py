# Точка входа FastAPI
import logging

from fastapi import FastAPI

from backend.app.db.infrastructure.database import engine
from backend.app.db.infrastructure.orm import Base

from routers import api_router
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


@app.get("/health_check/")
async def root():
    return {"message": "Alive"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
