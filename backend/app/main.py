# Точка входа FastAPI
from fastapi import FastAPI

from routers import api_router
from config import settings  # [import-not-found]

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")


@app.get("health_check")
async def root():
    return {"message": "Alive"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
