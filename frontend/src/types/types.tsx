interface SearchOptions {
    must_have: string[];
    should_have: string[];
    must_not_have: string[];
}


export interface Search {
    filters: {
        skills: SearchOptions;
        summary: SearchOptions;
        description: SearchOptions;
        demographics: {
            age_range: {
                from_value: number,
                to: number
            },
            locations: string[]
        };
        experience_vacancy: {
            min_years: number,
            max_years: number
        };
        experience_resume: {
            min_years: number,
            max_years: number
        };
        salary: {
            min_salary: number,
            max_salary: number
        };
        employment: {
            types: []
        }
    }
}

// Интерфейс для навыка
export interface Skill {
    skill_name: string;
    description: string;
    experience_age: number;
}

// Интерфейс для найденного резюме
export interface FoundResume {
    title: any;
    user_id: number;
    resume_id: number;
    summary: string;
    age: number;
    location: string;
    salary_from: number;
    salary_to: number;
    employment_type: string;
    experience_age: number;
    status: string;
    skills: Skill[];
    score: number;
}

// Интерфейс для найденной вакансии
export interface FoundVacancy {
    title: any;
    employer_id: number;
    vacancy_id: number;
    summary: string;
    experience_age_from: number;
    experience_age_to: number;
    location: string;
    salary_from: number;
    salary_to: number;
    employment_type: string;
    work_mode: string;
    skills: Skill[];
    score: number;
}

// Интерфейс для описания резюме, получаемого от сервера
export interface ResumeDescriptionResponse {
    resume_description: {
        candidate_id: number;
        title: string;
        summary: string;
        experience_age: number;
        location: string;
        salary_from: number;
        salary_to: number;
        employment_type: string;
        status: string;
        id: number;
    };
    skills: Skill[];
    candidate: {
        id: number;
        first_name: string;
        last_name: string;
        age: number;
        phone: number;
        user_id: number;
    };
}

export interface VacancyDescriptionResponse {
    vacancy_description: {
        employer_id: number;
        title: string;
        summary: string;
        experience_age_from: number;
        experience_age_to: number;
        location: string;
        salary_from: number;
        salary_to: number;
        employment_type: string;
        work_mode: string;
        id: number;
    };
    skills: {
        vacancy_id: number;
        skill_name: string;
        description: string;
    }[];
    employer: {
        id: number;
        first_name: string;
        last_name: string;
        phone: number;
    };
}

export const createSearch = (): Search => {
    return {
        filters: {
            skills: {must_have: [], should_have: [], must_not_have: []},
            summary: {must_have: [], should_have: [], must_not_have: []},
            description: {must_have: [], should_have: [], must_not_have: []},
            demographics: {age_range: {from_value: 0, to: 0}, locations: []},
            experience_vacancy: {min_years: 0, max_years: 0},
            experience_resume: {min_years: 0, max_years: 0},
            salary: {min_salary: 0, max_salary: 0},
            employment: {types: []}
        }
    }
};
