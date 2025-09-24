from sqlalchemy import Column, String, Integer, Numeric, Text, ForeignKey
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

    # Связь: у кандидата может быть несколько резюме
    resumes = relationship("ResumeORM", back_populates="candidate")


class ResumeORM(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)  # например "Backend Developer"
    summary = Column(Text, nullable=True)  # soft skills описание
    candidate = relationship("CandidateORM", back_populates="resumes")

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
    email = Column(String(50), nullable=True)
    phone = Column(Numeric(20), nullable=True)

    # Связь: у работодателя может быть несколько вакансий
    vacancies = relationship("VacancyORM", back_populates="employer")


class VacancyORM(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(Integer, ForeignKey("employers.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)  # например "Middle Python Developer"
    description = Column(Text, nullable=True)  # soft skills / культура / команда
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
