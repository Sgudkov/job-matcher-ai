import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.domain.unit_of_work import UnitOfWork
from backend.app.models.employer import EmployerCreate, EmployerUpdate


class TestDBEmployer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Создаем мок для сессии и session_factory
        self.db_mock = MagicMock(spec=AsyncSession)
        self.session_factory_mock = MagicMock(return_value=self.db_mock)

        # Создаем реальный UnitOfWork с мок session_factory
        self.uow = UnitOfWork(self.session_factory_mock)

        # Заменяем репозиторий на мок
        self.employers_repo_mock = AsyncMock()
        self.uow.employers = self.employers_repo_mock

        # Тестовые данные
        self.test_employer_data = EmployerCreate(
            first_name="John",
            last_name="Doe",
            company_name="FooBar",
            email="john@example.com",
            phone=1234567890,
        )
        self.test_employer_db = MagicMock()
        self.test_employer_db.id = 1
        self.test_employer_db.first_name = "John"
        self.test_employer_db.last_name = "Doe"
        self.test_employer_db.company_name = "FooBar"
        self.test_employer_db.email = "john@example.com"
        self.test_employer_db.phone = 1234567890

    async def test_create_employer(self):
        # Arrange
        self.employers_repo_mock.add.return_value = self.test_employer_db

        # Act
        employer_db = await self.uow.employers.add(self.test_employer_data)

        # Assert
        self.employers_repo_mock.add.assert_awaited_once_with(self.test_employer_data)
        self.assertEqual(employer_db.id, 1)
        self.assertEqual(employer_db.first_name, self.test_employer_data.first_name)
        self.assertEqual(employer_db.company_name, self.test_employer_data.company_name)

    async def test_get_employer(self):
        # Arrange
        self.employers_repo_mock.get.return_value = self.test_employer_db

        # Act
        employer_get = await self.uow.employers.get(id_=1)

        # Assert
        self.employers_repo_mock.get.assert_awaited_once_with(id_=1)
        self.assertEqual(employer_get.first_name, self.test_employer_db.first_name)
        self.assertEqual(employer_get.id, 1)

    async def test_update_employer(self):
        # Arrange
        update_data = EmployerUpdate(
            first_name="John",
            last_name="Doe",
            company_name="FooBar Inc.",
            email="john@example.com",
            phone=1234567890,
            id=1,
        )
        updated_employer = MagicMock()
        updated_employer.id = 1
        updated_employer.company_name = "FooBar Inc."
        updated_employer.first_name = "John"  # остальные поля остаются
        updated_employer.last_name = "Doe"

        self.employers_repo_mock.update.return_value = updated_employer

        # Act
        employer_updated = await self.uow.employers.update(id_=1, obj=update_data)

        # Assert
        self.employers_repo_mock.update.assert_awaited_once_with(id_=1, obj=update_data)
        self.assertEqual(employer_updated.company_name, "FooBar Inc.")
        self.assertEqual(employer_updated.id, 1)

    async def test_delete_employer(self):
        # Arrange
        self.employers_repo_mock.remove.return_value = True

        # Act
        result = await self.uow.employers.remove(id_=1)

        # Assert
        self.employers_repo_mock.remove.assert_awaited_once_with(id_=1)
        self.assertTrue(result)
