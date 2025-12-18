import unittest
from unittest.mock import AsyncMock
from backend.app.models.candidate import CandidateCreate


class TestDBSimple(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Просто создаем AsyncMock - он автоматически имеет все методы
        self.uow_mock = AsyncMock()

        # Настраиваем возвращаемые значения для методов UOW
        self.uow_mock.__aenter__.return_value = self.uow_mock
        self.uow_mock.__aexit__.return_value = None

        # Мок для репозитория
        self.candidates_mock = AsyncMock()
        self.candidates_mock.add.return_value = 1
        self.candidates_mock.get.return_value = CandidateCreate(
            first_name="test", last_name="test", age=20, email="test", phone=123
        )
        self.candidates_mock.update.return_value = CandidateCreate(
            first_name="updated", last_name="test", age=20, email="test", phone=123
        )
        self.candidates_mock.remove.return_value = CandidateCreate(
            first_name="deleted", last_name="test", age=20, email="test", phone=123
        )

        self.uow_mock.candidates = self.candidates_mock

    async def test_create_candidate(self):
        async with self.uow_mock as uow:
            candidate = CandidateCreate(
                first_name="test", last_name="test", age=20, email="test", phone=123
            )
            candidate_id = await uow.candidates.add(candidate)

            self.candidates_mock.add.assert_awaited_once_with(candidate)
            self.assertEqual(candidate_id, 1)

    async def test_all_methods(self):
        async with self.uow_mock as uow:
            # Test create
            candidate = CandidateCreate(
                first_name="test", last_name="test", age=20, email="test", phone=123
            )
            candidate_id = await uow.candidates.add(candidate)
            self.assertEqual(candidate_id, 1)

            # Test get
            candidate = await uow.candidates.get(1)
            self.assertEqual(candidate.first_name, "test")

            # Test update
            updated_candidate = await uow.candidates.update(1, candidate)
            self.assertEqual(updated_candidate.first_name, "updated")

            # Test remove
            removed_candidate = await uow.candidates.remove(1)
            self.assertEqual(removed_candidate.first_name, "deleted")
