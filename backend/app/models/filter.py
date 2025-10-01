from pydantic import BaseModel
from typing import List, Optional


class RangeFilter(BaseModel):
    from_value: Optional[int] = None
    to: Optional[int] = None


class SkillSearch(BaseModel):
    must_have: List[str] = []
    should_have: List[str] = []
    must_not_have: List[str] = []


class DemographicFilter(BaseModel):
    age_range: Optional[RangeFilter] = None
    locations: List[str] = []


class ExperienceFilter(BaseModel):
    min_years: Optional[int] = None
    max_years: Optional[int] = None


class SalaryFilter(BaseModel):
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class EmploymentFilter(BaseModel):
    types: List[str] = []


class SearchFilters(BaseModel):
    skills: Optional[SkillSearch] = None
    summary: Optional[SkillSearch] = None
    description: Optional[SkillSearch] = None
    demographics: Optional[DemographicFilter] = None
    experience_vacancy: Optional[ExperienceFilter] = None
    experience_resume: Optional[ExperienceFilter] = None
    salary: Optional[SalaryFilter] = None
    employment: Optional[EmploymentFilter] = None


class SearchRequest(BaseModel):
    filters: SearchFilters
