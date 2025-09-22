from dataclasses import dataclass, field
from uuid import uuid4, UUID


@dataclass
class Candidate:
    user_id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    hard_skill: str = ""
    soft_skill: str = ""


@dataclass
class Employer:
    user_id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: int = 0
    hard_skill: str = ""
    soft_skill: str = ""
