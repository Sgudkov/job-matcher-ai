# Работа с Qdrant и БД
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import QdrantCollection
from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import qdrant_api
from backend.app.db.infrastructure.orm import CandidateORM, EmployerORM
from backend.app.models.candidate import (
    CandidateCreate,
    CandidateEmbedding,
    ResumeUpsert,
    ResumeBase,
    ResumeSkillBase,
    CandidateVector,
    ResumeCreate,
    CandidateBase,
)
from backend.app.models.employer import (
    EmployerCreate,
    EmployerEmbedding,
    EmployerVacancyUpsert,
    VacancyBase,
    VacancySkill,
    EmployerVector,
    VacancyCreate,
    EmployerBase,
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
    new_resume: ResumeUpsert, skills: list[ResumeSkillBase], db: AsyncSession
):
    uow = UnitOfWork(db)
    async with uow.transaction():
        candidate = CandidateBase.model_validate(
            await uow.candidates.get(id_=new_resume.candidate_id)
        )
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
            for key, value in new_resume.model_dump(exclude={"id"}).items():
                setattr(resume, key, value)
        else:
            resume_create = ResumeCreate(**new_resume.model_dump(exclude={"id"}))
            resume = await uow.resumes.add(resume_create)
            await uow.session.flush()
            resume = ResumeCreate.model_validate(resume)
            for skill in skills:
                skill.resume_id = resume.id

        if not resume:
            raise Exception("Upsert resume: Resume not found")

        # Удаление скиллов из БД и Qdrant
        if skills:
            await uow.resume_skills.remove_skills_by_resume_id(resume.id)

            await qdrant_api.remove_candidate_skills(candidate.id, resume.id)

            # Добавление скиллов
            for skill in skills:
                if skill.resume_id == resume.id:
                    await uow.resume_skills.add(skill)

        # векторизация
        embedding: CandidateEmbedding = await vectorize_candidate(
            CandidateVector(
                **candidate.model_dump(exclude={"resumes", "skills"}),
                resumes=[ResumeBase(**resume.model_dump())],
                skills=skills,
            )
        )
        # добавление векторов в Qdrant
        qdrant_api.add_vectors(
            collection_name=QdrantCollection.CANDIDATES.value,
            vectors=embedding.embeddings,
        )
    return resume


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
        employer = EmployerBase.from_orm(
            await uow.employers.get(id_=new_vacancy.employer_id)
        )
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
            for key, value in new_vacancy.model_dump(exclude={"id"}).items():
                setattr(vacancy, key, value)
        else:
            create_vacancy = VacancyCreate(**new_vacancy.dict(exclude={"id"}))
            vacancy = await uow.vacancies.add(create_vacancy)
            await uow.session.flush()
            vacancy = VacancyCreate.from_orm(vacancy)
            for skill in skills:
                skill.vacancy_id = vacancy.id

        if not vacancy:
            raise Exception("Upsert vacancy: Vacancy not found")

        # Удаление скиллов из БД и Qdrant
        if skills:
            await uow.vacancy_skills.remove_skills_by_vacancy_id(vacancy.id)

            await qdrant_api.remove_employer_skills(employer.id, vacancy.id)

            # Добавление скиллов
            for skill in skills:
                if skill.vacancy_id == vacancy.id:
                    await uow.vacancy_skills.add(skill)

        # векторизация
        embedding: EmployerEmbedding = await vectorize_employer(
            EmployerVector(
                **employer.model_dump(exclude={"vacancies", "skills"}),
                vacancies=[VacancyBase(**vacancy.model_dump())],
                skills=skills,
            )
        )
        # добавление векторов в Qdrant
        qdrant_api.add_vectors(
            collection_name=QdrantCollection.EMPLOYERS.value,
            vectors=embedding.embeddings,
        )
    return vacancy
