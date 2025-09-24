from dataclasses import field

from pydantic import BaseModel
from qdrant_client.http.models import PointStruct

from backend.app.models.candidate import CandidateBase
from backend.app.models.employer import EmployerBase


class CandidateMatch(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class EmployerMatch(BaseModel):
    embeddings: list[PointStruct] = field(default_factory=list)


class MatchCandidateResult(CandidateBase):
    pass


class MatchEmployerResult(EmployerBase):
    pass
