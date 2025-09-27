from fastapi import APIRouter
from routes.candidates import router as candidates_router
from routes.employers import router as employers_router
from routes.resumes import router as resumes_router
from routes.match import router_employers as match_employers
from routes.match import router_candidates as match_candidates

api_router = APIRouter()

api_router.include_router(candidates_router, tags=["candidates"])
api_router.include_router(employers_router, tags=["employers"])
api_router.include_router(match_employers, tags=["match"])
api_router.include_router(match_candidates, tags=["match"])
api_router.include_router(resumes_router, tags=["resumes"])
# Временно вынесли наружу
# api_router.include_router(embeddings_router, tags=["vectorization"])
