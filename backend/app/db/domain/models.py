from dataclasses import dataclass, field
from uuid import uuid4, UUID

from qdrant_client.http.models import PointStruct


@dataclass
class Candidate:
    user_id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    hard_skill: str = ""
    embedding_hard: list[PointStruct] = field(default_factory=list)
    soft_skill: str = ""
    embedding_soft: list[PointStruct] = field(default_factory=list)


@dataclass
class Employer:
    user_id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    hard_skill: str = ""
    embedding_hard: list[PointStruct] = field(default_factory=list)
    soft_skill: str = ""
    embedding_soft: list[PointStruct] = field(default_factory=list)
