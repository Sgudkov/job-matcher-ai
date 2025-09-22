from fastapi import APIRouter
from routes.candidates import router as candidates_router
from routes.employers import router as employers_router

api_router = APIRouter()

api_router.include_router(candidates_router, tags=["candidates"])
api_router.include_router(employers_router, tags=["employers"])
# Временно вынесли наружу
# api_router.include_router(embeddings_router, tags=["vectorization"])
