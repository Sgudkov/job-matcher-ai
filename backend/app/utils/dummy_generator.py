import json

from backend.app.db.infrastructure.database import get_db
from backend.app.db.infrastructure.members import SqlCandidate, SqlEmployer
from backend.app.models.candidate import CandidateCreate
from backend.app.models.employer import EmployerCreate
from backend.app.services.storage import register_candidate, register_employer


async def generate_candidates():
    db_gen = get_db()

    with open("dummy_candidate_data.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
    async for session in db_gen:
        sql_candidate = SqlCandidate(session)
        for candidate in candidates:
            await register_candidate(
                sql_candidate, session, CandidateCreate(**candidate)
            )


async def generate_employers():
    db_gen = get_db()

    with open("dummy_employer_data.json", "r", encoding="utf-8") as f:
        employers = json.load(f)
    async for session in db_gen:
        sql_employer = SqlEmployer(session)
        for employer in employers:
            await register_employer(sql_employer, session, EmployerCreate(**employer))


async def match():
    pass
    # match_service = MatchingService(qdrant_api=qdrant_api)
    # best_employers = match_service.find_best_employers_for_candidate(
    #     user_id="acc386f1-9a9a-4a53-9410-08297982b651"
    # )

    # db_gen = get_db()

    # async for session in db_gen:
    #     sql_employer = SqlEmployer(session)
    #     for employer in best_employers:
    #         employer_match = await sql_employer.get_by_employer_id(employer[0])
    #         print(employer_match.user_id, employer_match.hard_skill, employer_match.soft_skill)


if __name__ == "__main__":
    import asyncio

    asyncio.run(match())
    # asyncio.run(generate_candidates())
    # asyncio.run(generate_employers())
