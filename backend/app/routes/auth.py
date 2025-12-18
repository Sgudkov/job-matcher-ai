# backend/app/api/auth.py
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from backend.app.config import settings
from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.db.infrastructure.database import get_db
from backend.app.models.auth import Token, User, TokenData
from backend.app.models.candidate import CandidateCreate, RegisterCandidate
from backend.app.models.employer import EmployerCreate, RegisterEmployer
from backend.app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# Временная база пользователей (замените на реальную БД)
fake_users_db = {
    "testuser": {
        "id": "2026",
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": get_password_hash("test"),
        "disabled": False,
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user(db, email: str) -> User:
    uow = UnitOfWork(db)
    user = await uow.user.get_by_email(email=email)
    return user


async def authenticate_user(db, email: str, password: str):
    user = await get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Определяем роль пользователя
    uow = UnitOfWork(db)
    candidate = await uow.candidates.get_by_user_id(user_id=user.id)
    employer = await uow.employers.get_by_user_id(user_id=user.id)

    if candidate:
        role = "candidate"
    elif employer:
        role = "employer"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated role (candidate or employer)",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/candidate")
async def register_candidate(
    data: RegisterCandidate, db: AsyncSession = Depends(get_db)
):
    """Регистрация кандидата"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            # Проверка email
            existing_user = await uow.user.get_by_email(email=data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Создание UserORM
            hashed_password = get_password_hash(data.password)
            new_user = await uow.user.add(
                User(email=data.email, password=hashed_password, is_active=True)
            )
            await uow.session.flush()  # Важно! Получить ID

            # Создание CandidateORM со связью
            new_candidate = await uow.candidates.add(
                CandidateCreate(
                    user_id=new_user.id,  # Связываем с UserORM
                    first_name=data.first_name,
                    last_name=data.last_name,
                    age=data.age,
                    phone=data.phone,
                )
            )
            await uow.session.flush()  # Получить ID кандидата

        return {
            "message": "Candidate registered successfully",
            "email": data.email,
            "role": "candidate",
            "candidate_id": new_candidate.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/employer")
async def register_employer(data: RegisterEmployer, db: AsyncSession = Depends(get_db)):
    """Регистрация работодателя"""
    try:
        uow = UnitOfWork(db)
        async with uow.transaction():
            # Проверка email
            existing_user = await uow.user.get_by_email(email=data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Создание UserORM
            hashed_password = get_password_hash(data.password)
            new_user = await uow.user.add(
                User(email=data.email, password=hashed_password, is_active=True)
            )
            await uow.session.flush()  # Важно! Получить ID

            # Создание EmployerORM со связью
            new_employer = await uow.employers.add(
                EmployerCreate(
                    user_id=new_user.id,  # Связываем с UserORM
                    first_name=data.first_name,
                    last_name=data.last_name,
                    company_name=data.company_name,
                    phone=data.phone,
                )
            )
            await uow.session.flush()  # Получить ID работодателя

        return {
            "message": "Employer registered successfully",
            "email": data.email,
            "role": "company",
            "employer_id": new_employer.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering employer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify-token")
async def verify_token(current_user: TokenData = Depends(get_current_active_user)):
    """Проверка валидности токена"""
    return {
        "message": "Token is valid",
    }
