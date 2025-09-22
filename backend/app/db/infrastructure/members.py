from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.domain.members import CandidateMembers, EmployerMembers
from backend.app.db.domain.models import Candidate, Employer
from backend.app.db.infrastructure.orm import CandidateORM, EmployerORM


class SqlCandidate(CandidateMembers):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, candidate: Candidate) -> CandidateORM:
        candidate_orm = CandidateORM(
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            phone=candidate.phone,
            soft_skill=candidate.soft_skill,
            hard_skill=candidate.hard_skill,
        )

        self.session.add(candidate_orm)
        return candidate_orm

    async def get(self, id_key: int) -> Candidate:
        candidate_orm = await self.session.get(CandidateORM, id_key)
        if candidate_orm is None:
            raise ValueError(f"Candidate with id {id_key} not found")
        return Candidate(
            user_id=UUID(str(candidate_orm.user_id)),
            first_name=candidate_orm.first_name,
            last_name=candidate_orm.last_name,
            email=candidate_orm.email,
            phone=candidate_orm.phone,
            soft_skill=candidate_orm.soft_skill,
            hard_skill=candidate_orm.hard_skill,
        )

    async def get_all(self) -> list[Candidate]:
        stmt = select(CandidateORM)
        candidates_orm = await self.session.execute(stmt)
        if candidates_orm is None:
            raise ValueError("""Candidates not found""")
        return [
            Candidate(
                user_id=UUID(str(candidate_orm.user_id)),
                first_name=candidate_orm.first_name,
                last_name=candidate_orm.last_name,
                email=candidate_orm.email,
                phone=candidate_orm.phone,
            )
            for candidate_orm in candidates_orm.scalars().all()
        ]


class SqlEmployer(EmployerMembers):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, employer: Employer) -> EmployerORM:
        employer_orm = EmployerORM(
            first_name=employer.first_name,
            last_name=employer.last_name,
            email=employer.email,
            phone=employer.phone,
            soft_skill=employer.soft_skill,
            hard_skill=employer.hard_skill,
        )

        self.session.add(employer_orm)
        return employer_orm

    async def get(self, id_key: int) -> Employer:
        employer_orm = await self.session.get(EmployerORM, id_key)
        return Employer(
            user_id=UUID(str(employer_orm.employer_id)),
            first_name=employer_orm.first_name,
            last_name=employer_orm.last_name,
            email=employer_orm.email,
            phone=employer_orm.phone,
            hard_skill=employer_orm.hard_skill,
            soft_skill=employer_orm.soft_skill,
        )

    async def get_all(self) -> list[Employer]:
        stmt = select(EmployerORM)
        employers_orm = await self.session.execute(stmt)
        return [
            Employer(
                first_name=employer_orm.first_name,
                last_name=employer_orm.last_name,
                email=employer_orm.email,
                phone=employer_orm.phone,
                hard_skill=employer_orm.hard_skill,
                soft_skill=employer_orm.soft_skill,
            )
            for employer_orm in employers_orm.scalars().all()
        ]
