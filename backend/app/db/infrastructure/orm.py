from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    Float,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CandidateORM(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String(50), nullable=True)
    phone = Column(Numeric(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # Связь: у кандидата может быть несколько резюме
    resumes = relationship("ResumeORM", back_populates="candidate")


class ResumeORM(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)  # например "Backend Developer"
    summary = Column(Text, nullable=True)  # soft skills описание
    experience_age = Column(Integer, nullable=True)
    location = Column(String(50), nullable=True)
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    employment_type = Column(String(50), nullable=True)
    candidate = relationship("CandidateORM", back_populates="resumes")
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    status = Column(String(20), default="active")

    # Связь: у резюме несколько hard skills
    skills = relationship("ResumeSkillORM", back_populates="resume")


class ResumeSkillORM(Base):
    __tablename__ = "resume_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    skill_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)  # что делал с этим навыком
    resume = relationship("ResumeORM", back_populates="skills")


class EmployerORM(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    company_name = Column(String(100), nullable=True)
    email = Column(String(50), nullable=True)
    phone = Column(Numeric(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # Связь: у работодателя может быть несколько вакансий
    vacancies = relationship("VacancyORM", back_populates="employer")


class VacancyORM(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(Integer, ForeignKey("employers.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)  # например "Middle Python Developer"
    description = Column(Text, nullable=True)  # soft skills / культура / команда
    experience_age_from = Column(Integer, nullable=True)
    experience_age_to = Column(Integer, nullable=True)
    location = Column(String(50), nullable=True)
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    employment_type = Column(String(50), nullable=True)
    work_mode = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    employer = relationship("EmployerORM", back_populates="vacancies")

    # Связь: у вакансии несколько требуемых hard skills
    skills = relationship("VacancySkillORM", back_populates="vacancy")


class VacancySkillORM(Base):
    __tablename__ = "vacancy_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"))
    skill_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)  # уточнение, зачем нужен этот навык
    vacancy = relationship("VacancyORM", back_populates="skills")


class MatchORM(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.id", ondelete="CASCADE"))
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    is_new = Column(Boolean, default=True)


class FavoriteResumeORM(Base):
    __tablename__ = "favorite_resumes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("employers.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    created_at = Column(DateTime, default=datetime.now())


class FavoriteVacancyORM(Base):
    __tablename__ = "favorite_vacancies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("candidates.id"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"))
    created_at = Column(DateTime, default=datetime.now())
