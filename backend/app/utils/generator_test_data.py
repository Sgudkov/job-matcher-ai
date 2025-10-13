"""
Модуль для генерации и загрузки тестовых данных
Загружает данные из JSON файлов в базу данных через API
"""

import json
from pathlib import Path

import httpx
from typing import Dict, Any, List

from qdrant_client.http.models import models

from backend.app.config import QdrantCollection, MembersDataType
from backend.app.db.infrastructure.database import qdrant_api


async def call_api_httpx(
    url: str,
    method: str = "GET",
    data: Dict = None,  # type: ignore[assignment]
) -> Dict[str, Any]:
    """
    Вызов API с использованием httpx

    :param url: адрес API
    :param method: метод запроса
    :param data: данные для запроса
    :return: ответ API в формате json
    """
    async with httpx.AsyncClient(
        verify=False,
        timeout=httpx.Timeout(
            connect=30.0,  # время на установку соединения
            read=60.0,  # время на чтение ответа
            write=30.0,  # время на отправку запроса
            pool=30.0,  # время на получение соединения из пула
        ),
    ) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, params=data)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()  # Выбрасывает исключение для 4xx/5xx статусов
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise


def load_json_file(filename: str) -> List[Dict[str, Any]]:
    """
    Загрузка данных из JSON файла

    :param filename: имя файла в папке utils
    :return: список данных из JSON
    """
    current_dir = Path(__file__).parent
    file_path = current_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def get_user_token(base_url: str, email: str, password: str) -> str | None:
    """
    Получение токена для пользователя

    :param base_url: базовый URL API
    :param email: email пользователя
    :param password: пароль пользователя
    :return: токен или None
    """
    try:
        url = f"{base_url}/api/v1/auth/token"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                data={
                    "username": email,
                    "password": password,
                },  # OAuth2 использует form data
            )
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
    except Exception as e:
        print(f"[ERROR] Не удалось получить токен для {email}: {e}")
        return None


async def register_candidates(
    base_url: str = "http://127.0.0.1:8000",
) -> tuple[Dict[str, int], Dict[str, str]]:
    """
    Регистрация кандидатов из candidates.json

    :param base_url: базовый URL API
    :return: кортеж (словарь {email: candidate_id}, словарь {email: token})
    """
    print("Загрузка кандидатов...")
    candidates_data = load_json_file("candidates.json")
    candidate_ids = {}
    candidate_tokens = {}

    for idx, candidate in enumerate(candidates_data, 1):
        try:
            url = f"{base_url}/api/v1/auth/register/candidate"
            response = await call_api_httpx(url, method="POST", data=candidate)
            candidate_id = response.get("candidate_id")
            if candidate_id:
                candidate_ids[candidate["email"]] = candidate_id
                print(
                    f"[OK] Кандидат {candidate['first_name']} {candidate['last_name']} зарегистрирован (ID: {candidate_id})"
                )

                # Получаем токен для этого кандидата
                token = await get_user_token(
                    base_url, candidate["email"], candidate["password"]
                )
                if token:
                    candidate_tokens[candidate["email"]] = token
            else:
                print(
                    f"[WARNING] Кандидат зарегистрирован, но ID не получен: {candidate['email']}"
                )
        except Exception as e:
            error_msg = str(e)
            if "Email already registered" in error_msg or "400" in error_msg:
                # Пользователь уже существует - получаем токен
                print(f"[INFO] Кандидат {candidate['email']} уже зарегистрирован")
                candidate_ids[candidate["email"]] = idx
                token = await get_user_token(
                    base_url, candidate["email"], candidate["password"]
                )
                if token:
                    candidate_tokens[candidate["email"]] = token
            else:
                print(f"[ERROR] Ошибка регистрации кандидата {candidate['email']}: {e}")

    return candidate_ids, candidate_tokens


async def register_employers(
    base_url: str = "http://127.0.0.1:8000",
) -> tuple[Dict[str, int], Dict[str, str]]:
    """
    Регистрация работодателей из employers.json

    :param base_url: базовый URL API
    :return: кортеж (словарь {email: employer_id}, словарь {email: token})
    """
    print("\nЗагрузка работодателей...")
    employers_data = load_json_file("employers.json")
    employer_ids = {}
    employer_tokens = {}

    for idx, employer in enumerate(employers_data, 1):
        try:
            url = f"{base_url}/api/v1/auth/register/employer"
            response = await call_api_httpx(url, method="POST", data=employer)
            employer_id = response.get("employer_id")
            if employer_id:
                employer_ids[employer["email"]] = employer_id
                print(
                    f"[OK] Работодатель {employer['company_name']} зарегистрирован (ID: {employer_id})"
                )

                # Получаем токен для этого работодателя
                token = await get_user_token(
                    base_url, employer["email"], employer["password"]
                )
                if token:
                    employer_tokens[employer["email"]] = token
            else:
                print(
                    f"[WARNING] Работодатель зарегистрирован, но ID не получен: {employer['email']}"
                )
        except Exception as e:
            error_msg = str(e)
            if "Email already registered" in error_msg or "400" in error_msg:
                # Работодатель уже существует - получаем токен
                print(f"[INFO] Работодатель {employer['email']} уже зарегистрирован")
                employer_ids[employer["email"]] = idx
                token = await get_user_token(
                    base_url, employer["email"], employer["password"]
                )
                if token:
                    employer_tokens[employer["email"]] = token
            else:
                print(
                    f"[ERROR] Ошибка регистрации работодателя {employer['email']}: {e}"
                )

    return employer_ids, employer_tokens


async def create_resumes(
    base_url: str = "http://127.0.0.1:8000",
    candidate_ids: Dict[str, int] = None,
    candidate_tokens: Dict[str, str] = None,
) -> None:
    """
    Создание резюме из resumes.json

    :param base_url: базовый URL API
    :param candidate_ids: словарь {email: candidate_id} из регистрации
    :param candidate_tokens: словарь {email: token} из регистрации
    """
    print("\nЗагрузка резюме...")
    resumes_data = load_json_file("resumes.json")
    candidates_list = load_json_file("candidates.json")

    if not candidate_ids:
        print("[WARNING] Список candidate_ids пуст, используются ID из JSON")

    for idx, resume_data in enumerate(resumes_data):
        try:
            # Создаем копию, чтобы не изменять оригинальные данные
            resume = resume_data.copy()
            # Извлекаем skills из resume
            skills = resume.pop("skills", [])

            # Получаем правильный candidate_id и токен из словаря
            candidate_email = None
            token = None

            if candidate_ids and idx < len(candidates_list):
                candidate_email = candidates_list[idx]["email"]
                real_candidate_id = candidate_ids.get(candidate_email)
                if real_candidate_id:
                    resume["candidate_id"] = real_candidate_id
                else:
                    print(f"[WARNING] Не найден candidate_id для {candidate_email}")

                # Получаем токен
                if candidate_tokens:
                    token = candidate_tokens.get(candidate_email)

            if not token:
                print(
                    f"[ERROR] Нет токена для создания резюме '{resume.get('title', 'Unknown')}'"
                )
                continue

            # Создаем резюме - FastAPI ожидает JSON с двумя ключами
            url = f"{base_url}/api/v1/resumes/"

            async with httpx.AsyncClient(timeout=60.0) as client:
                # Отправляем как JSON body с токеном авторизации
                response = await client.post(
                    url,
                    json={"candidate_resume": resume, "skills": skills},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()

            print(
                f"[OK] Резюме '{resume['title']}' создано для кандидата ID: {resume['candidate_id']}"
            )
        except httpx.HTTPStatusError as e:
            print(
                f"[HTTP ERROR] Создание резюме '{resume_data.get('title', 'Unknown')}': {e.response.status_code}"
            )
            print(f"  Детали: {e.response.text}")
        except Exception as e:
            print(
                f"[ERROR] Создание резюме '{resume_data.get('title', 'Unknown')}': {e}"
            )


async def create_vacancies(
    base_url: str = "http://127.0.0.1:8000",
    employer_ids: Dict[str, int] = None,
    employer_tokens: Dict[str, str] = None,
) -> None:
    """
    Создание вакансий из vacancies.json

    :param base_url: базовый URL API
    :param employer_ids: словарь {email: employer_id} из регистрации
    :param employer_tokens: словарь {email: token} из регистрации
    """
    print("\nЗагрузка вакансий...")
    vacancies_data = load_json_file("vacancies.json")
    employers_list = load_json_file("employers.json")

    if not employer_ids:
        print("[WARNING] Список employer_ids пуст, используются ID из JSON")

    # Создаем маппинг employer_id из JSON -> реальный employer_id и email
    employer_id_mapping = {}
    employer_email_mapping = {}
    if employer_ids:
        for idx, employer in enumerate(employers_list, 1):
            real_id = employer_ids.get(employer["email"])
            if real_id:
                employer_id_mapping[idx] = real_id
                employer_email_mapping[idx] = employer["email"]

    for vacancy_data in vacancies_data:
        try:
            # Создаем копию, чтобы не изменять оригинальные данные
            vacancy = vacancy_data.copy()
            # Извлекаем skills из vacancy
            skills = vacancy.pop("skills", [])

            # Получаем правильный employer_id и токен из маппинга
            old_employer_id = vacancy.get("employer_id")
            employer_email = employer_email_mapping.get(old_employer_id)
            token = None

            if old_employer_id in employer_id_mapping:
                vacancy["employer_id"] = employer_id_mapping[old_employer_id]

                # Получаем токен
                if employer_tokens and employer_email:
                    token = employer_tokens.get(employer_email)
            elif employer_ids:
                print(
                    f"[WARNING] Не найден employer_id для старого ID {old_employer_id}"
                )

            if not token:
                print(
                    f"[ERROR] Нет токена для создания вакансии '{vacancy.get('title', 'Unknown')}'"
                )
                continue

            # Создаем вакансию - FastAPI ожидает JSON с двумя ключами
            url = f"{base_url}/api/v1/vacancies/"

            async with httpx.AsyncClient(timeout=60.0) as client:
                # Отправляем как JSON body с токеном авторизации
                response = await client.post(
                    url,
                    json={"vacancy": vacancy, "skills": skills},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()

            print(
                f"[OK] Вакансия '{vacancy['title']}' создана для работодателя ID: {vacancy['employer_id']}"
            )
        except httpx.HTTPStatusError as e:
            print(
                f"[HTTP ERROR] Создание вакансии '{vacancy_data.get('title', 'Unknown')}': {e.response.status_code}"
            )
            print(f"  Детали: {e.response.text}")
        except Exception as e:
            print(
                f"[ERROR] Создание вакансии '{vacancy_data.get('title', 'Unknown')}': {e}"
            )


async def load_all_test_data(base_url: str = "http://127.0.0.1:8000") -> None:
    """
    Загрузка всех тестовых данных в базу

    :param base_url: базовый URL API
    """
    print("=" * 60)
    print("Начало загрузки тестовых данных")
    print("=" * 60)

    try:
        # 1. Регистрация кандидатов и получение токенов
        candidate_ids, candidate_tokens = await register_candidates(base_url)

        # 2. Регистрация работодателей и получение токенов
        employer_ids, employer_tokens = await register_employers(base_url)

        # 3. Создание резюме (передаем реальные candidate_ids и токены)
        await create_resumes(base_url, candidate_ids, candidate_tokens)

        # 4. Создание вакансий (передаем реальные employer_ids и токены)
        await create_vacancies(base_url, employer_ids, employer_tokens)

        print("\n" + "=" * 60)
        print("[SUCCESS] Все тестовые данные успешно загружены!")
        print("=" * 60)
        print("Статистика:")
        print(f"  - Кандидатов: {len(candidate_ids)}")
        print(f"  - Работодателей: {len(employer_ids)}")
        print(f"  - Резюме: {len(load_json_file('resumes.json'))}")
        print(f"  - Вакансий: {len(load_json_file('vacancies.json'))}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Ошибка при загрузке данных: {e}")
        raise


async def remove_qdrant_candidate_skills() -> None:
    """
    Удалить все skills для соискателей
    """
    qdrant_api.client.delete(
        collection_name=QdrantCollection.CANDIDATES.value,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchText(text=MembersDataType.HARD_SKILL.value),
                    )
                ]
            ),
        ),
    )

    qdrant_api.client.delete(
        collection_name=QdrantCollection.CANDIDATES.value,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchText(text=MembersDataType.SOFT_SKILL.value),
                    )
                ]
            ),
        ),
    )


async def remove_qdrant_employer_skills() -> None:
    """
    Удалить все skills для работодателей
    """
    qdrant_api.client.delete(
        collection_name=QdrantCollection.EMPLOYERS.value,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchText(text=MembersDataType.HARD_SKILL.value),
                    )
                ]
            ),
        ),
    )

    qdrant_api.client.delete(
        collection_name=QdrantCollection.EMPLOYERS.value,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchText(text=MembersDataType.SOFT_SKILL.value),
                    )
                ]
            ),
        ),
    )


async def clear_qdrant_data() -> None:
    """
    Очистка данных из Qdrant (опционально)
    """
    print("[CLEAR] Очистка данных из Qdrant...")
    await remove_qdrant_candidate_skills()
    await remove_qdrant_employer_skills()
    print("[OK] Данные из Qdrant очищены")


if __name__ == "__main__":
    import asyncio
    import sys

    # Использование:
    # python generator_test_data.py                    - загрузить все данные
    # python generator_test_data.py --clear-qdrant     - очистить Qdrant
    # python generator_test_data.py --url http://...   - указать другой URL API

    base_url = "http://127.0.0.1:8000"

    # Парсинг аргументов командной строки
    if "--clear-qdrant" in sys.argv:
        asyncio.run(clear_qdrant_data())
    elif "--url" in sys.argv:
        url_index = sys.argv.index("--url") + 1
        if url_index < len(sys.argv):
            base_url = sys.argv[url_index]
        asyncio.run(load_all_test_data(base_url))
    else:
        asyncio.run(load_all_test_data(base_url))
