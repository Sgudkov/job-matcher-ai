from abc import ABC, abstractmethod

from backend.app.db.domain.models import Candidate, Employer


class CandidateMembers(ABC):
    @abstractmethod
    async def add(self, candidate: Candidate):
        pass

    @abstractmethod
    async def get(self, user_id: int) -> Candidate:
        pass

    @abstractmethod
    async def get_all(self) -> list[Candidate]:
        pass


class EmployerMembers(ABC):
    @abstractmethod
    async def add(self, employer: Employer):
        pass

    @abstractmethod
    async def get(self, employer_id: int) -> Employer:
        pass

    @abstractmethod
    async def get_all(self) -> list[Employer]:
        pass
