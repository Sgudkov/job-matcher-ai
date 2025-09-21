from backend.app.db.domain.members import CandidateMembers, EmployerMembers
from backend.app.db.domain.models import Candidate, Employer


class MembersService:
    def __init__(self, candidate: CandidateMembers, employer: EmployerMembers):
        self.candidate = candidate
        self.employer = employer

    async def create_candidate(self, first_name: str, last_name: str, email: str, phone: str) -> Candidate:
        candidate = Candidate(first_name=first_name, last_name=last_name, email=email, phone=phone)
        await self.candidate.add(candidate)
        return candidate

    async def create_employer(self, first_name: str, last_name: str, email: str, phone: str) -> Employer:
        employer = Employer(first_name=first_name, last_name=last_name, email=email,
                            phone=phone)
        await self.employer.add(employer)
        return employer
