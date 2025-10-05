"""
Модуль для генерации тестовых данных
"""

import json

import httpx
from typing import Dict, Any

from qdrant_client.http.models import models

from backend.app.config import QdrantCollection, MembersDataType
from backend.app.db.infrastructure.database import qdrant_api
from backend.app.models.candidate import CandidateCreate, ResumeUpsert


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


async def create_candidate():
    """
    Создае тестового соискателя со всеми skills
    """
    with open("fake_candidates.json", "r", encoding="utf-8") as f:
        new_data: list = json.load(f)  # type: ignore[annotation-unchecked]
        with open("fake_resumes.json", "r", encoding="utf-8") as r:
            resumes: list = json.load(r)

        for data, resume in zip(new_data, resumes):
            candidate = CandidateCreate(**data)
            url = "http://127.0.0.1:8000/api/v1/candidates/"
            response = await call_api_httpx(url, method="POST", data=candidate.dict())
            candidate_id = response.get("id")

            new_resume = ResumeUpsert(**resume.get("candidate_resume"))
            new_resume.candidate_id = candidate_id
            skills: list = resume.get("skills")
            new_skills: list = [skill for skill in skills]
            url = "http://127.0.0.1:8000/api/v1/resumes/"
            await call_api_httpx(
                url,
                method="POST",
                data={
                    "candidate_resume": new_resume.model_dump(),
                    "skills": new_skills,
                },
            )


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


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_candidate())
    # asyncio.run(remove_qdrant_candidate_skills())
