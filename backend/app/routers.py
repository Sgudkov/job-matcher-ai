from fastapi import APIRouter
from app.routes.candidates import router as candidates_router
from app.routes.employers import router as employers_router
from app.routes.resumes import router as resumes_router
from app.routes.match import router as match_router
from app.routes.match import recalc_router
from app.routes.vacancies import router as vacancies_router
from app.routes.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(candidates_router)
api_router.include_router(employers_router)
api_router.include_router(match_router)
api_router.include_router(recalc_router)
api_router.include_router(resumes_router)
api_router.include_router(vacancies_router)
api_router.include_router(auth_router)
# Временно вынесли наружу
# api_router.include_router(embeddings_router, tags=["vectorization"])
