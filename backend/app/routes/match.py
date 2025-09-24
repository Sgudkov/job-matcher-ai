# Эндпоинт для поиска матчей
import logging

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.infrastructure.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router_employers = APIRouter(prefix="/employers", tags=["employers"])


@router_employers.get("/{employer_id}/recommendations")
async def get_employer_recommendations(
    employer_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        return "OK"
        # response: [MatchCandidateResult] = []
        # candidate_members = SqlCandidate(db)
        # match_service = MatchingService(qdrant_api=qdrant_api)
        # best_employers = match_service.find_best_candidates_for_employer(
        #     employer_id=employer_id
        # )

        # for employer in best_employers:
        #     response.append(await candidate_members.get_by_candidate_id(candidate_id=employer[0]))

        # return response
    except Exception as e:
        logger.error(f"Error getting employer: {e}")
        raise HTTPException(status_code=500, detail="Error getting employer")


router_candidates = APIRouter(prefix="/candidates", tags=["candidates"])


@router_candidates.get("/{candidate_id}/recommendations")
async def get_candidate_recommendations(
    candidate_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        return "OK"
        # response: [MatchEmployerResult] = []
        # employer_members = SqlEmployer(db)
        # match_service = MatchingService(qdrant_api=qdrant_api)
        # best_employers = match_service.find_best_employers_for_candidate(
        #     user_id=candidate_id
        # )
        #
        # # for employer in best_employers:
        # #     response.append(await employer_members.get_by_employer_id(employer_id=employer[0]))
        #
        # return response
    except Exception as e:
        logger.error(f"Error getting candidate: {e}")
        raise HTTPException(status_code=500, detail="Error getting candidate")
