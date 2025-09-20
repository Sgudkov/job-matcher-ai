from pydantic import BaseModel


class CandidateBase(BaseModel):
    id: int = 0
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    hard_skill: str = ""
    soft_skill: str = ""


class CandidateEmbedding(CandidateBase):
    embedding: list
