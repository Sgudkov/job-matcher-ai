from dataclasses import field
from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None


class User(BaseModel):
    id: int | None = None
    password: str
    email: str
    is_active: bool = True
    created_at: datetime | None = field(default_factory=datetime.now)
    updated_at: datetime | None = field(default_factory=datetime.now)


class UserInDB(User):
    hashed_password: str
