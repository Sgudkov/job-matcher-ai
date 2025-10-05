// app/vacancies/page.tsx
'use client';

import { useState } from 'react';
import '../../styles/globals.css';
const mockVacancies = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'TechCorp',
    salary: 150000,
    location: 'Москва',
    employment: 'Полная занятость',
    experience: '1-3 года'
  },
  {
    id: '2',
    title: 'Backend Developer',
    company: 'DataSystems',
    salary: 180000,
    location: 'Удаленно',
    employment: 'Удаленная работа',
    experience: '3-6 лет'
  },
  {
    id: '3',
    title: 'UX Designer',
    company: 'DesignStudio',
    salary: 120000,
    location: 'Санкт-Петербург',
    employment: 'Полная занятость',
    experience: '1-3 года'
  }
];

export default function VacanciesPage() {
  const [search, setSearch] = useState('');
  const [selectedEmployment, setSelectedEmployment] = useState<string[]>([]);

  const filteredVacancies = mockVacancies.filter(vacancy => {
    const matchesSearch = vacancy.title.toLowerCase().includes(search.toLowerCase()) ||
                         vacancy.company.toLowerCase().includes(search.toLowerCase());

    const matchesEmployment = selectedEmployment.length === 0 ||
                             selectedEmployment.includes(vacancy.employment);

    return matchesSearch && matchesEmployment;
  });

  const employmentTypes = ['Полная занятость', 'Частичная занятость', 'Удаленная работа', 'Проектная работа'];

  return (
    <div className="vacancies-container">
      {/* Шапка с поиском */}
      <div className="vacancies-header">
        <div className="vacancies-header-content">
          <h1 className="vacancies-title">Вакансии</h1>
          <input
            type="text"
            placeholder="Поиск вакансий, компаний..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="vacancies-search-input"
          />
        </div>
      </div>

      {/* Основной контент */}
      <div className="vacancies-main-content">

        {/* Фильтры */}
        <div className="vacancies-filters-sidebar">
          <div className="vacancies-filters-card">
            <h3 className="vacancies-filter-title">Фильтры</h3>

            <div style={{ marginBottom: '20px' }}>
              <h4 className="filter-section-title">Тип занятости</h4>
              <div className="vacancies-checkbox-group">
                {employmentTypes.map((type) => (
                  <label key={type} className="vacancies-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedEmployment.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedEmployment([...selectedEmployment, type]);
                        } else {
                          setSelectedEmployment(selectedEmployment.filter(t => t !== type));
                        }
                      }}
                      className="vacancies-checkbox"
                    />
                    {type}
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={() => setSelectedEmployment([])}
              className="vacancies-reset-button"
            >
              Сбросить фильтры
            </button>
          </div>
        </div>

        {/* Список вакансий */}
        <div className="vacancies-content">
          <div className="vacancies-center">

            <div className="vacancies-stats">
              Найдено вакансий: {filteredVacancies.length}
            </div>

            <div className="vacancies-list">
              {filteredVacancies.map((vacancy) => (
                <div key={vacancy.id} className="vacancy-card">
                  <h3 className="vacancy-title">{vacancy.title}</h3>
                  <div className="vacancy-details">
                    <div className="vacancy-company-info">
                      <p className="vacancy-company">{vacancy.company}</p>
                      <div className="vacancy-meta-info">
                        <span>{vacancy.location}</span>
                        <span>•</span>
                        <span>{vacancy.employment}</span>
                        <span>•</span>
                        <span>{vacancy.experience}</span>
                      </div>
                    </div>
                    <div className="vacancy-salary-container">
                      <p className="vacancy-salary">
                        {vacancy.salary.toLocaleString()} ₽
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredVacancies.length === 0 && (
              <div className="vacancies-no-results">
                <p className="vacancies-no-results-title">Вакансии не найдены</p>
                <p className="vacancies-no-results-subtitle">Попробуйте изменить параметры поиска</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
