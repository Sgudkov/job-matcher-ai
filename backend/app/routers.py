from fastapi import APIRouter
from routes.candidates import router as candidates_router  # [import-not-found]
from services.embeddings import router as embeddings_router # [import-not-found]

api_router = APIRouter()

api_router.include_router(candidates_router, tags=["candidates"])
# Временно вынесли наружу
api_router.include_router(embeddings_router, tags=["vectorization"])
