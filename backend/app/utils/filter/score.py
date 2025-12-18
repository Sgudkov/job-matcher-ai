import re
from typing import List, TypeVar, Type

from qdrant_client.http.models import ScoredPoint, Filter
from rapidfuzz import fuzz

from backend.app.config import MembersDataType
from backend.app.models.match import (
    EmployerMatch,
    CandidateMatch,
    SkillMatch,
    ResumeMatchResponse,
    VacancyMatchResponse,
)

T = TypeVar("T", EmployerMatch, CandidateMatch)


class FilterScore:
    def __init__(
        self,
        points: List["ScoredPoint"],
        hard_filter: Filter,
        soft_filter: Filter,
        hard_vector_not: list[float] | None,
        soft_vector_not: list[float] | None,
        entity_cls: Type[T],
        averaged_scores: dict[int, float],
        similarity_threshold: float = 0.4,
    ):
        self.points = points
        self.hard_filter = hard_filter
        self.soft_filter = soft_filter
        self.complex_scores: dict[set, list] = {}
        self.decrease_score: dict[int, float] = {}
        self.increase_score: dict[int, float] = {}
        self.entity_cls: Type[T] = entity_cls
        self.hard_vector_not = hard_vector_not
        self.soft_vector_not = soft_vector_not
        self.similarity_threshold = similarity_threshold
        self.averaged_scores = averaged_scores
        self.result_scores: dict[int, float] = {}
        self.hards: dict[int, list] = {}
        self.softs: dict = {}

    async def calc_score(self):
        # Соберем результат в {ключ,score} -> payload
        for res in self.points:
            keys = await self.entity_cls(**res.payload).get_key_name_value()
            if res.payload.get("type", "") == "soft_skill":
                self.softs[keys[1]] = res.payload

                curr_vector = res.vector.get(MembersDataType.SOFT_SKILL.value, [])

                # По сходству COS, будем штрафовать
                if (curr_vector and self.soft_vector_not) and (
                    cos_sim := self._cosine_similarity(
                        self.soft_vector_not, curr_vector
                    )
                ) > self.similarity_threshold:
                    penalty = (cos_sim - self.similarity_threshold) * 0.25
                    self.decrease_score[keys[1]] = (
                        self.decrease_score.get(keys[1], 0) + penalty
                    )

            elif res.payload.get("type", "") == "hard_skill":
                self.hards.setdefault(keys[1], []).append(res.payload)

                curr_vector = res.vector.get(MembersDataType.HARD_SKILL.value, [])

                skill_name = res.payload.get("skill_name_norm", "")

                # Найдем вхождения

                # За каждое совпадение будем штрафовать
                if self.hard_filter and self.hard_filter.must_not:
                    matches = sum(
                        bool(
                            re.search(
                                rf"\b{re.escape(must_not.match.text)}\b", skill_name
                            )
                        )
                        for must_not in self.hard_filter.must_not
                    )
                    fuzzy_score = sum(
                        fuzz.partial_ratio(must_not.match.text, skill_name)
                        for must_not in self.hard_filter.must_not
                    )

                    if matches or fuzzy_score > 85:
                        self.decrease_score[keys[1]] = (
                            self.decrease_score.get(keys[1], 0) + 0.1 * matches
                        )

                # За каждое совпадение будем увеличивать score
                if self.hard_filter and self.hard_filter.must:
                    matches = sum(
                        bool(
                            re.search(rf"\b{re.escape(must.match.text)}\b", skill_name)
                        )
                        for must in self.hard_filter.must
                    )
                    fuzzy_score = sum(
                        fuzz.partial_ratio(must.match.text, skill_name)
                        for must in self.hard_filter.must
                    )

                    if matches or fuzzy_score > 85:
                        self.increase_score[keys[1]] = (
                            self.decrease_score.get(keys[1], 0) + 0.1
                        )

                # По сходству COS, будем штрафовать
                if (self.hard_vector_not and curr_vector) and (
                    cos_sim := self._cosine_similarity(
                        self.hard_vector_not, curr_vector
                    )
                ) > self.similarity_threshold:
                    penalty = (cos_sim - self.similarity_threshold) * 0.25
                    self.decrease_score[keys[1]] = (
                        self.decrease_score.get(keys[1], 0) + penalty
                    )

            self.result_scores[keys[1]] = self.averaged_scores.get(keys[1], 0)

    def assemble_results(self, first_call: bool) -> list[T]:
        result = []

        for s_key, soft in self.softs.items():
            skills: list[SkillMatch] = []
            for k, v in self.hards.items():
                if k == s_key:
                    skills.extend([SkillMatch(**skill2) for skill2 in v])

            max_penalty = 0.5
            penalty = 0.0

            if first_call:
                score = 0.0
            else:
                score = self.result_scores.get(s_key, 0.0)

                # Получим все штрафы
                if s_key in self.decrease_score:
                    penalty += self.decrease_score[s_key]

                # Ограничим максимум
                penalty = min(penalty, max_penalty)

                # Если ключ в поиске, увеличиваем score
                score += self.increase_score.get(s_key, 0)

                score = score * (1 - penalty)

            if self.entity_cls is CandidateMatch:
                result.append(
                    ResumeMatchResponse(
                        user_id=soft.get("user_id", ""),
                        resume_id=soft.get("resume_id", ""),
                        title=soft.get("title", ""),
                        summary=soft.get("summary", ""),
                        age=soft.get("age", ""),
                        location=soft.get("location", ""),
                        salary_from=soft.get("salary_from", ""),
                        salary_to=soft.get("salary_to", ""),
                        employment_type=soft.get("employment_type", ""),
                        experience_age=soft.get("experience_age", ""),
                        status=soft.get("status", ""),
                        skills=skills,
                        score=score,
                    )
                )
            elif self.entity_cls is EmployerMatch:
                result.append(
                    VacancyMatchResponse(
                        employer_id=soft.get("employer_id", ""),
                        vacancy_id=soft.get("vacancy_id", ""),
                        title=soft.get("title", ""),
                        summary=soft.get("summary", ""),
                        experience_age_from=soft.get("experience_age_from", ""),
                        experience_age_to=soft.get("experience_age_to", ""),
                        location=soft.get("location", ""),
                        salary_from=soft.get("salary_from", ""),
                        salary_to=soft.get("salary_to", ""),
                        employment_type=soft.get("employment_type", ""),
                        work_mode=soft.get("work_mode", ""),
                        skills=skills,
                        score=score,
                    )
                )
        return result

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Вычисляет косинусную схожесть между векторами."""
        import numpy as np

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
