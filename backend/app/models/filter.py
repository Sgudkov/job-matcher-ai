from pydantic import BaseModel, fields
from typing import List, Optional


class RangeFilter(BaseModel):
    from_value: Optional[int] = fields.Field(default_factory=int)
    to: Optional[int] = fields.Field(default_factory=int)


class SkillSearch(BaseModel):
    must_have: List[str] = fields.Field(default_factory=list)
    should_have: List[str] = fields.Field(default_factory=list)
    must_not_have: List[str] = fields.Field(default_factory=list)


class DemographicFilter(BaseModel):
    age_range: Optional[RangeFilter] = fields.Field(default_factory=RangeFilter)
    locations: List[str] = fields.Field(default_factory=list)


class ExperienceFilter(BaseModel):
    min_years: Optional[int] = fields.Field(default_factory=int)
    max_years: Optional[int] = fields.Field(default_factory=int)


class SalaryFilter(BaseModel):
    min_salary: Optional[int] = fields.Field(default_factory=int)
    max_salary: Optional[int] = fields.Field(default_factory=int)


class EmploymentFilter(BaseModel):
    types: List[str] = fields.Field(default_factory=list)


class SearchFilters(BaseModel):
    skills: Optional[SkillSearch] = fields.Field(default_factory=SkillSearch)
    summary: Optional[SkillSearch] = fields.Field(default_factory=SkillSearch)
    description: Optional[SkillSearch] = fields.Field(default_factory=SkillSearch)
    demographics: Optional[DemographicFilter] = fields.Field(
        default_factory=DemographicFilter
    )
    experience: Optional[ExperienceFilter] = fields.Field(
        default_factory=ExperienceFilter
    )
    salary: Optional[SalaryFilter] = fields.Field(default_factory=SalaryFilter)
    employment: Optional[EmploymentFilter] = fields.Field(
        default_factory=EmploymentFilter
    )


class SearchRequest(BaseModel):
    filters: SearchFilters
