from typing import Tuple

from numpy import ndarray
from qdrant_client.http.models import Filter, models

from app.models.filter import SearchRequest, SearchFilters


class QdrantFilterBuilder:
    def __init__(self, config, embedding_system):
        self.config = config
        self.embedding_system = embedding_system

    async def build(
        self, search_request: SearchRequest
    ) -> Tuple[
        Filter | None,
        Filter | None,
        ndarray | None,
        ndarray | None,
        ndarray | None,
        ndarray | None,
    ]:
        # Весь код из _build_qdrant_filters
        soft_skills_must: list[models.FieldCondition] = []
        soft_skills_should: list[models.FieldCondition] = []
        soft_skills_must_not: list[models.FieldCondition] = []

        hard_skills_must: list[models.FieldCondition] = []
        hard_skills_should: list[models.FieldCondition] = []
        hard_skills_must_not: list[models.FieldCondition] = []
        filters: SearchFilters = search_request.filters

        # Векторизуем hard и soft скиллы

        skills_must = filters.skills.must_have if filters.skills else []
        skills_should = filters.skills.should_have if filters.skills else []
        description_must = filters.description.must_have if filters.description else []
        description_should = (
            filters.description.should_have if filters.description else []
        )

        # Векторизуем по требуемым навыкам в вакансии/резюме
        text_hard = " ".join(
            [
                f"{', '.join([s.lower().strip() for s in skills_must])}",
                f"{', '.join([s.lower().strip() for s in skills_should])}",
                f"{', '.join([s.lower().strip() for s in description_must])}",
                f"{', '.join([s.lower().strip() for s in description_should])}",
            ]
        ).strip()

        if text_hard:
            hard_vector = self.embedding_system.encode_long_text(
                model=self.config.HARD_MODEL, text=text_hard
            )
        else:
            hard_vector = None

        summary_must = filters.summary.must_have if filters.summary else []
        summary_should = filters.summary.should_have if filters.summary else []

        # Векторизуем по описанию в вакансии/резюме
        text_soft = " ".join(
            [
                f"{', '.join([s.lower().strip() for s in summary_must])}",
                f"{','.join([s.lower().strip() for s in summary_should])}",
            ]
        ).strip()

        if text_soft:
            soft_vector = self.embedding_system.encode_long_text(
                model=self.config.SOFT_MODEL, text=text_soft
            )
        else:
            soft_vector = None

        # Векторизуем skills must_not_have для исключения в post-обработке
        skills_must_not = filters.skills.must_not_have if filters.skills else []
        hard_vector_not = []
        for skill in skills_must_not:
            vector = self.embedding_system.encode_long_text(
                model=self.config.HARD_MODEL, text=skill.lower()
            )
            hard_vector_not.append(vector)

        if not hard_vector_not:
            hard_vector_not = None  # type: ignore[assignment]

        # Векторизуем summary must_not_have для исключения в post-обработке
        summary_must_not = filters.summary.must_not_have if filters.summary else []
        soft_vector_not = []
        for summary in summary_must_not:
            vector = self.embedding_system.encode_long_text(
                model=self.config.SOFT_MODEL, text=summary.lower()
            )
            soft_vector_not.append(vector)

        if not soft_vector_not:
            soft_vector_not = None  # type: ignore[assignment]

        # Соберем фильтры

        # 1 Hard skills фильтры

        # Дополнительно жестко ограничим навыки, если они пришли в фильтре
        if filters.skills:
            if filters.skills.must_have:
                hard_skills_must.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.must_have
                    ]
                )

            # MatchText работает как полнотекстовый поиск
            if filters.skills.must_not_have:
                hard_skills_must_not.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.must_not_have
                    ]
                )

            if filters.skills.should_have:
                hard_skills_should.extend(
                    [
                        models.FieldCondition(
                            key="skill_name_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.skills.should_have
                    ]
                )

        # 2 Soft skills фильтры

        # Summary
        if filters.summary:
            if filters.summary.must_have:
                soft_skills_should.extend(
                    [
                        models.FieldCondition(
                            key="summary_norm",
                            match=models.MatchText(text=skill.lower().strip()),
                        )
                        for skill in filters.summary.must_have
                    ]
                )
        # if filters.summary.must_not_have:
        #     soft_skills_must_not.extend(
        #         [
        #             models.FieldCondition(
        #                 key="summary_norm",
        #                 match=models.MatchText(text=skill.lower()),
        #             )
        #             for skill in filters.summary.must_not_have
        #         ]
        #     )

        # Добавили в векторизацию
        # if filters.summary.should_have:
        #     soft_skills_should.extend(
        #         [
        #             models.FieldCondition(
        #                 key="summary_norm",
        #                 match=models.MatchText(text=skill.lower()),
        #             )
        #             for skill in filters.summary.should_have
        #         ]
        #     )

        # Исключим из результатов стоп слова
        if filters.description:
            if filters.description.must_not_have:
                soft_skills_must_not.extend(
                    [
                        models.FieldCondition(
                            key="description_norm",
                            match=models.MatchText(text=skill.lower()),
                        )
                        for skill in filters.description.must_not_have
                    ]
                )

        # 3 Демографические фильтры
        if filters.demographics:
            if filters.demographics.age_range:
                age_range = filters.demographics.age_range
                if age_range.from_value or age_range.to:
                    soft_skills_must.append(
                        models.FieldCondition(
                            key="age",
                            range=models.Range(
                                gte=age_range.from_value or None,
                                lte=age_range.to or None,
                            ),
                        )
                    )

            if filters.demographics.locations:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="location",
                        match=models.MatchAny(any=filters.demographics.locations),
                    )
                )

        # 4 Опыт в вакансии
        if filters.experience_vacancy:
            exp = filters.experience_vacancy
            if exp.min_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_from",
                        range=models.Range(gte=exp.min_years or None),
                    )
                )

            if exp.max_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age_to",
                        range=models.Range(lte=exp.max_years or None),
                    )
                )

        # 5 Опыт в резюме
        if filters.experience_resume:
            exp = filters.experience_resume
            if exp.min_years or exp.max_years:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="experience_age",
                        range=models.Range(
                            gte=exp.min_years or None, lte=exp.max_years or None
                        ),
                    )
                )

        # 6 Зарплата
        if filters.salary:
            salary = filters.salary
            if salary.min_salary:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="salary_from",
                        range=models.Range(gte=salary.min_salary or None),
                    )
                )
            if salary.max_salary:
                soft_skills_must.append(
                    models.FieldCondition(
                        key="salary_to",
                        range=models.Range(lte=salary.max_salary or None),
                    )
                )

        # 7 Тип занятости
        if filters.employment and filters.employment.types:
            soft_skills_must.append(
                models.FieldCondition(
                    key="employment_type_norm",
                    match=models.MatchAny(any=filters.employment.types),
                )
            )

        filter_hard = {}
        filter_soft = {}

        if hard_skills_must:
            filter_hard["must"] = hard_skills_must
        if hard_skills_should:
            filter_hard["should"] = hard_skills_should
            # filter_hard["min_should"] = 1  # type: ignore[assignment]
        if hard_skills_must_not:
            filter_hard["must_not"] = hard_skills_must_not

        if soft_skills_must:
            filter_soft["must"] = soft_skills_must
        if soft_skills_should:
            filter_soft["should"] = soft_skills_should
            # Минимум одно should-условие должно выполниться
            # filter_soft["min_should"] = 1  # type: ignore[assignment]
        if soft_skills_must_not:
            filter_soft["must_not"] = soft_skills_must_not

        soft_filter = Filter(**filter_soft) if filter_soft else None
        hard_filter = Filter(**filter_hard) if filter_hard else None

        return (
            soft_filter,
            hard_filter,
            soft_vector,
            hard_vector,
            hard_vector_not,
            soft_vector_not,
        )
