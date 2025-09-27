# Работа с Qdrant и БД
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import QdrantCollection, MembersDataType
from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import qdrant_api
from backend.app.db.infrastructure.orm import CandidateORM, EmployerORM
from backend.app.models.candidate import (
    CandidateCreate,
    CandidateEmbedding,
    CandidateResumeUpsert,
    ResumeBase,
    ResumeSkill,
    CandidateVector,
    ResumeCreate,
)
from backend.app.models.employer import (
    EmployerCreate,
    EmployerEmbedding,
    EmployerVacancyUpsert,
    VacancyBase,
    VacancySkill,
    EmployerVector,
    VacancyCreate,
)
from backend.app.services.embeddings import vectorize_candidate, vectorize_employer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание коллекций
for collection in QdrantCollection:
    collection_name = collection.value

    vector_size = 0

    if qdrant_api.client.collection_exists(collection_name):
        continue

    if not qdrant_api.create_collection(collection_name):
        logger.error(f"Error creating collection {collection_name}")


async def register_candidate(
    candidate: CandidateCreate, db: AsyncSession
) -> CandidateORM:
    uow = UnitOfWork(db)
    async with uow.transaction():
        new_candidate = await uow.candidates.add(candidate)
    return new_candidate


async def upsert_resume(
    new_resume: CandidateResumeUpsert, skills: list[ResumeSkill], db: AsyncSession
):
    uow = UnitOfWork(db)
    async with uow.transaction():
        candidate = await uow.candidates.get(id_=new_resume.candidate_id)
        if not candidate:
            raise Exception("Upsert resume: Candidate not found")

        resumes = await uow.resumes.get_by_candidate_id(
            candidate_id=new_resume.candidate_id
        )

        if resumes is None:
            resumes = []

        for resume in resumes:
            if resume.id == new_resume.id:
                break
        else:
            resume = None

        if resume:
            resume.title = new_resume.title
            resume.summary = new_resume.summary
            resume.experience_age = new_resume.experience_age
            resume.location = new_resume.location
            resume.salary_from = new_resume.salary_from
            resume.salary_to = new_resume.salary_to
            resume.employment_type = new_resume.employment_type
        else:
            create_resume = new_resume.model_dump(exclude={"id"})
            create_resume = ResumeCreate(**create_resume)
            resume = await uow.resumes.add(create_resume)
            await uow.session.flush()
            for skill in skills:
                skill.resume_id = resume.id

        if not resume:
            raise Exception("Upsert resume: Resume not found")

        # Удаление скиллов из БД и Qdrant
        if skills:
            await uow.resume_skills.remove_skills_by_resume_id(resume.id)

            keys = {
                "type": MembersDataType.SOFT_SKILL.value,
                "user_id": candidate.id,
                "resume_id": resume.id,
            }

            qdrant_api.remove_points(
                collection_name=QdrantCollection.CANDIDATES.value, kwargs=keys
            )

            keys["type"] = MembersDataType.HARD_SKILL.value
            qdrant_api.remove_points(
                collection_name=QdrantCollection.CANDIDATES.value, kwargs=keys
            )

            # Добавление скиллов
            for skill in skills:
                if skill.resume_id == resume.id:
                    await uow.resume_skills.add(skill)

        # векторизация
        embedding: CandidateEmbedding = await vectorize_candidate(
            CandidateVector(
                id=candidate.id,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                email=candidate.email,
                phone=candidate.phone,
                age=candidate.age,
                resumes=[ResumeBase(**resume.__dict__)],
                skills=skills,
            )
        )
        # добавление векторов в Qdrant
        qdrant_api.add_vectors(
            collection_name=QdrantCollection.CANDIDATES.value,
            vectors=embedding.embeddings,
        )
    return candidate


async def register_employer(employer: EmployerCreate, db: AsyncSession) -> EmployerORM:
    uow = UnitOfWork(db)
    async with uow.transaction():
        new_employer = await uow.employers.add(employer)
        return new_employer


async def upsert_vacancy(
    new_vacancy: EmployerVacancyUpsert, skills: list[VacancySkill], db: AsyncSession
):
    uow = UnitOfWork(db)
    async with uow.transaction():
        employer = await uow.employers.get(id_=new_vacancy.employer_id)
        if not employer:
            raise Exception("Upsert vacancy: Vacancy not found")

        vacancies = await uow.vacancies.get_by_employer_id(
            employer_id=new_vacancy.employer_id
        )

        for vacancy in vacancies:
            if vacancy.id == new_vacancy.id:
                break
        else:
            vacancy = None

        if vacancy:
            vacancy.title = new_vacancy.title
            vacancy.description = new_vacancy.description
            vacancy.experience_age_from = new_vacancy.experience_age_from
            vacancy.experience_age_to = new_vacancy.experience_age_to
            vacancy.location = new_vacancy.location
            vacancy.salary_from = new_vacancy.salary_from
            vacancy.salary_to = new_vacancy.salary_to
            vacancy.employment_type = new_vacancy.employment_type
        else:
            create_vacancy = VacancyCreate(**new_vacancy.dict(exclude={"id"}))
            vacancy = await uow.vacancies.add(create_vacancy)
            await uow.session.flush()
            for skill in skills:
                skill.vacancy_id = vacancy.id

        if not vacancy:
            raise Exception("Upsert vacancy: Vacancy not found")

        # Удаление скиллов из БД и Qdrant
        if skills:
            await uow.vacancy_skills.remove_skills_by_vacancy_id(vacancy.id)

            keys = {
                "type": MembersDataType.SOFT_SKILL.value,
                "employer_id": employer.id,
                "vacancy_id": vacancy.id,
            }

            qdrant_api.remove_points(
                collection_name=QdrantCollection.EMPLOYERS.value, kwargs=keys
            )

            keys["type"] = MembersDataType.HARD_SKILL.value
            qdrant_api.remove_points(
                collection_name=QdrantCollection.EMPLOYERS.value, kwargs=keys
            )

            # Добавление скиллов
            for skill in skills:
                if skill.vacancy_id == vacancy.id:
                    await uow.vacancy_skills.add(skill)

        # векторизация
        embedding: EmployerEmbedding = await vectorize_employer(
            EmployerVector(
                id=employer.id,
                first_name=employer.first_name,
                last_name=employer.last_name,
                email=employer.email,
                phone=employer.phone,
                vacancies=[VacancyBase(**vacancy.__dict__)],
                skills=skills,
            )
        )
        # добавление векторов в Qdrant
        qdrant_api.add_vectors(
            collection_name=QdrantCollection.EMPLOYERS.value,
            vectors=embedding.embeddings,
        )
    return employer
