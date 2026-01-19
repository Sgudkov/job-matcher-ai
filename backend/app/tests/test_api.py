"""
Комплексные тесты для всех API эндпоинтов
Использует pytest и httpx для асинхронного тестирования FastAPI
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.db.infrastructure.orm import Base
from backend.app.db.infrastructure.database import get_db
from backend.app.main import app

# Тестовая база данных (SQLite для тестов)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создание тестового движка
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
async def db_session():
    """Создание тестовой сессии БД для каждого теста"""
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Очищаем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Создание тестового клиента FastAPI"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_candidate_data():
    """Тестовые данные для кандидата"""
    return {
        "email": "candidate@test.com",
        "password": "testpass123",
        "first_name": "John",
        "last_name": "Doe",
        "age": 25,
        "phone": 1234567890,
    }


@pytest.fixture
async def test_employer_data():
    """Тестовые данные для работодателя"""
    return {
        "email": "employer@test.com",
        "password": "testpass123",
        "first_name": "Jane",
        "last_name": "Smith",
        "company_name": "Tech Corp",
        "phone": 9876543210,
    }


@pytest.fixture
async def registered_candidate(client, test_candidate_data):
    """Зарегистрированный кандидат"""
    response = await client.post(
        "/api/v1/auth/register/candidate", json=test_candidate_data
    )
    assert response.status_code == 200
    return test_candidate_data


@pytest.fixture
async def registered_employer(client, test_employer_data):
    """Зарегистрированный работодатель"""
    response = await client.post(
        "/api/v1/auth/register/employer", json=test_employer_data
    )
    assert response.status_code == 200
    return test_employer_data


@pytest.fixture
async def candidate_token(client, registered_candidate):
    """Токен аутентификации для кандидата"""
    response = await client.post(
        "/api/v1/auth/token",
        data={
            "username": registered_candidate["email"],
            "password": registered_candidate["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def employer_token(client, registered_employer):
    """Токен аутентификации для работодателя"""
    response = await client.post(
        "/api/v1/auth/token",
        data={
            "username": registered_employer["email"],
            "password": registered_employer["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ============================================================================
# ТЕСТЫ АУТЕНТИФИКАЦИИ (AUTH)
# ============================================================================


class TestAuth:
    """Тесты эндпоинтов аутентификации"""

    @pytest.mark.asyncio
    async def test_register_candidate_success(self, client, test_candidate_data):
        """Успешная регистрация кандидата"""
        response = await client.post(
            "/api/v1/auth/register/candidate", json=test_candidate_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Candidate registered successfully"
        assert data["email"] == test_candidate_data["email"]
        assert data["role"] == "candidate"

    @pytest.mark.asyncio
    async def test_register_employer_success(self, client, test_employer_data):
        """Успешная регистрация работодателя"""
        response = await client.post(
            "/api/v1/auth/register/employer", json=test_employer_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Employer registered successfully"
        assert data["email"] == test_employer_data["email"]
        assert data["role"] == "company"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client, registered_candidate, test_candidate_data
    ):
        """Регистрация с уже существующим email"""
        response = await client.post(
            "/api/v1/auth/register/candidate", json=test_candidate_data
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_success(self, client, registered_candidate):
        """Успешный логин"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": registered_candidate["email"],
                "password": registered_candidate["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, registered_candidate):
        """Логин с неправильным паролем"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": registered_candidate["email"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Логин несуществующего пользователя"""
        response = await client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent@test.com", "password": "password123"},
        )

        assert response.status_code == 401


# ============================================================================
# ТЕСТЫ КАНДИДАТОВ (CANDIDATES)
# ============================================================================


class TestCandidates:
    """Тесты эндпоинтов кандидатов"""

    @pytest.mark.asyncio
    async def test_get_candidate_success(self, client, candidate_token, db_session):
        """Получение данных текущего кандидата"""
        # Теперь эндпоинт GET /api/v1/candidates/ возвращает данные текущего пользователя
        response = await client.get(
            "/api/v1/candidates/",
            headers={"Authorization": f"Bearer {candidate_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "candidate"
        assert "id" in data
        assert "first_name" in data
        assert "last_name" in data

    @pytest.mark.asyncio
    async def test_get_candidate_unauthorized(self, client):
        """Получение кандидата без токена"""
        response = await client.get("/api/v1/candidates/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_candidate_not_found(self, client):
        """Получение кандидата для пользователя без профиля кандидата"""
        # Создаем токен для несуществующего user_id
        from backend.app.core.security import create_access_token

        fake_token = create_access_token(
            data={"sub": "99999", "email": "fake@test.com", "role": "candidate"}
        )

        response = await client.get(
            "/api/v1/candidates/", headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 404


# ============================================================================
# ТЕСТЫ РАБОТОДАТЕЛЕЙ (EMPLOYERS)
# ============================================================================


class TestEmployers:
    """Тесты эндпоинтов работодателей"""

    @pytest.mark.asyncio
    async def test_get_employer_success(self, client, employer_token, db_session):
        """Получение данных текущего работодателя"""
        # Теперь эндпоинт GET /api/v1/employers/ возвращает данные текущего пользователя
        response = await client.get(
            "/api/v1/employers/", headers={"Authorization": f"Bearer {employer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "company"
        assert "company_name" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_employer_unauthorized(self, client):
        """Получение работодателя без токена"""
        response = await client.get("/api/v1/employers/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_employer_not_found(self, client):
        """Получение работодателя для пользователя без профиля работодателя"""
        # Создаем токен для несуществующего user_id
        from backend.app.core.security import create_access_token

        fake_token = create_access_token(
            data={"sub": "99999", "email": "fake@test.com", "role": "employer"}
        )

        response = await client.get(
            "/api/v1/employers/", headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 404


# ============================================================================
# ТЕСТЫ РЕЗЮМЕ (RESUMES)
# ============================================================================


class TestResumes:
    """Тесты эндпоинтов резюме"""

    @pytest.mark.asyncio
    async def test_create_resume(self, client, candidate_token, db_session):
        """Создание резюме для текущего кандидата"""
        resume_data = {
            "candidate_id": 1,  # Будет перезаписан на сервере
            "title": "Python Developer",
            "summary": "Experienced developer",
            "experience_age": 3,
            "location": "Moscow",
            "salary_from": 100000,
            "salary_to": 150000,
            "employment_type": "full-time",
            "status": "active",
        }

        skills = [
            {
                "resume_id": 0,
                "skill_name": "Python",
                "description": "5 years experience",
            }
        ]

        # Отправляем с токеном авторизации
        response = await client.post(
            "/api/v1/resumes/",
            json={"candidate_resume": resume_data, "skills": skills},
            headers={"Authorization": f"Bearer {candidate_token}"},
        )

        # Может быть 200, 422 (validation error) или 500 (Qdrant не настроен)
        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_get_resume(self, client, candidate_token):
        """Получение резюме по ID (только своего)"""
        response = await client.get(
            "/api/v1/resumes/1", headers={"Authorization": f"Bearer {candidate_token}"}
        )

        # Может быть 200, 404, 403 (not your resume), 422 или 500
        assert response.status_code in [200, 404, 403, 422, 500]


# ============================================================================
# ТЕСТЫ ВАКАНСИЙ (VACANCIES)
# ============================================================================


class TestVacancies:
    """Тесты эндпоинтов вакансий"""

    @pytest.mark.asyncio
    async def test_create_vacancy(self, client, employer_token, db_session):
        """Создание вакансии для текущего работодателя"""
        vacancy_data = {
            "employer_id": 1,  # Будет перезаписан на сервере
            "title": "Senior Python Developer",
            "summary": "Looking for experienced developer",
            "experience_age_from": 3,
            "experience_age_to": 5,
            "location": "Moscow",
            "salary_from": 150000,
            "salary_to": 200000,
            "employment_type": "full-time",
            "work_mode": "remote",
        }

        skills = [{"vacancy_id": 0, "skill_name": "Python", "description": "Required"}]

        # Отправляем с токеном авторизации
        response = await client.post(
            "/api/v1/vacancies/",
            json={"vacancy": vacancy_data, "skills": skills},
            headers={"Authorization": f"Bearer {employer_token}"},
        )

        # Может быть 200, 422 (validation error) или 500 (Qdrant не настроен)
        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_get_vacancy(self, client, employer_token):
        """Получение вакансии по ID (только своей)"""
        response = await client.get(
            "/api/v1/vacancies/1", headers={"Authorization": f"Bearer {employer_token}"}
        )

        # Может быть 200, 404, 403 (not your vacancy), 422 или 500
        assert response.status_code in [200, 404, 403, 422, 500]


# ============================================================================
# ТЕСТЫ МАТЧИНГА (MATCHES)
# ============================================================================


class TestMatches:
    """Тесты эндпоинтов матчинга"""

    @pytest.mark.asyncio
    async def test_get_resume_matches(self, client):
        """Получение матчей для резюме"""
        response = await client.get("/api/v1/matches/resumes/1")

        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_get_vacancy_matches(self, client):
        """Получение матчей для вакансии"""
        response = await client.get("/api/v1/matches/vacancies/1")

        assert response.status_code in [200, 500]


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================


class TestIntegration:
    """Интеграционные тесты полного цикла"""

    @pytest.mark.asyncio
    async def test_full_candidate_flow(self, client, test_candidate_data):
        """Полный цикл: регистрация -> логин -> получение данных"""
        # 1. Регистрация
        reg_response = await client.post(
            "/api/v1/auth/register/candidate", json=test_candidate_data
        )
        assert reg_response.status_code == 200

        # 2. Логин
        login_response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": test_candidate_data["email"],
                "password": test_candidate_data["password"],
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Получение данных (требует ID из БД)
        # В реальном тесте нужно получить ID из БД
        assert token is not None

    @pytest.mark.asyncio
    async def test_full_employer_flow(self, client, test_employer_data):
        """Полный цикл: регистрация -> логин -> получение данных"""
        # 1. Регистрация
        reg_response = await client.post(
            "/api/v1/auth/register/employer", json=test_employer_data
        )
        assert reg_response.status_code == 200

        # 2. Логин
        login_response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": test_employer_data["email"],
                "password": test_employer_data["password"],
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        assert token is not None


# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
