from uuid import uuid4

from sqlalchemy import Column, String, Integer, Numeric, Text, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CandidateORM(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, unique=True, index=True, nullable=False, default=uuid4)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    phone = Column(Numeric(20), nullable=True)
    soft_skill = Column(Text, nullable=True)
    hard_skill = Column(Text, nullable=True)


class EmployerORM(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(UUID, unique=True, index=True, nullable=False, default=uuid4)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    phone = Column(Numeric(20), nullable=True)
    soft_skill = Column(Text, nullable=True)
    hard_skill = Column(Text, nullable=True)
