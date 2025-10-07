// app/vacancies/page.tsx
'use client';

import { useState } from 'react';
import '../../styles/globals.css';
import { getSearchData } from '../../lib/api';
import { createSearch, FoundResume } from '../types/types';

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
  const [skillInputs, setSkillInputs] = useState({});
  const [summaryInputs, setSummaryInputs] = useState({});
  const [isSkillsExpanded, setIsSkillsExpanded] = useState(true);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(true);
  const [isSalaryExpanded, setIsSalaryExpanded] = useState(true);
  const [isExpirienceExpanded, setIsExperienceExpanded] = useState(true);
  const [filteredVacancies, setFilteredVacancies] = useState<FoundResume[]>([]);


  // const filteredVacancies = mockVacancies.filter(vacancy => {
  //   const matchesSearch = vacancy.title.toLowerCase().includes(search.toLowerCase()) ||
  //     vacancy.company.toLowerCase().includes(search.toLowerCase());

  //   const matchesEmployment = selectedEmployment.length === 0 ||
  //     selectedEmployment.includes(vacancy.employment);

  //   return matchesSearch && matchesEmployment;
  // });

  // Функция для переключения раздела навыков
  const toggleSkillsSection = () => {
    setIsSkillsExpanded(prev => !prev);
  };

  // Функция для переключения раздела суммарных требований
  const toggleSummarySection = () => {
    setIsSummaryExpanded(prev => !prev);
  };

  // Функция для переключения раздела зарплаты
  const toggleSalarySection = () => {
    setIsSalaryExpanded(prev => !prev);
  };

  // Функция для переключения раздела опыта
  const toggleExperienceSection = () => {
    setIsExperienceExpanded(prev => !prev);
  };



  // Функция для обработки изменения ввода навыков
  const handleSkillChange = (skillType: string, value: string) =>
    setSkillInputs(prevInputs => ({
      ...prevInputs,
      [skillType]: value
    }));

  // Функция для обработки изменения ввода суммарных требований
  const handleSummaryChange = (summaryType: string, value: string) =>
    setSummaryInputs(prevInputs => ({
      ...prevInputs,
      [summaryType]: value
    }));

  // Функция для обработки изменения ввода зарплаты
  const handleSalaryChange = (salaryType: string, value: string) =>
    setSummaryInputs(prevInputs => ({
      ...prevInputs,
      [salaryType]: value
    }));

  // Функция для обработки изменения ввода опыта
  const handleExperienceChange = (experienceType: string, value: string) =>
    setSummaryInputs(prevInputs => ({
      ...prevInputs,
      [experienceType]: value
    }));

  // Преобразует строку в массив навыков (разделитель - запятая)
  const getSkillsArray = (skillsString) => {
    return skillsString ? skillsString
      .split(',')
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0) : [];
  };

  const skillOption = ['Включить', 'Исключить'];
  const rangeOption = ['От', 'До'];

  const requestSearch = () => {
    const searchData = createSearch();

    searchData.filters.skills.must_have = getSkillsArray(skillInputs['Включить']);
    searchData.filters.skills.must_not_have = getSkillsArray(skillInputs['Исключить']);

    getSearchData(searchData).then((res) => { setFilteredVacancies(res); });

  };



  return (
    <div className="vacancies-container">
      {/* Шапка с поиском */}
      <div className="vacancies-header">
        <div className="vacancies-header-content">
          <input
            type="text"
            placeholder="Поиск"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="vacancies-search-input"
          />
          <button className="vacancies-search-button">Найти</button>

        </div>
      </div>

      {/* Основной контент */}
      <div className="vacancies-main-content">

        {/* Фильтры */}
        <div className="vacancies-filters-sidebar">
          <div className="vacancies-filters-card">
            <h3 className="vacancies-filter-title">Фильтры</h3>

            <div className="vacancies-filter-group">

              {/* Заголовок с кнопкой сворачивания */}
              {/* Раздел навыков */}
              <div className="filter-section-header" onClick={toggleSkillsSection}>
                <h4 className="filter-section-title">Навыки</h4>
                <span className="collapse-icon">
                  {isSkillsExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Содержимое секции */}
              {isSkillsExpanded && (
                <div className="filter-section-content">
                  {skillOption.map((type) => (
                    <div className='vacancies-filter-label'>
                      <span className='vacancies-filter-count'>
                        {type}
                        {/* ({getSkillsArray(skillInputs[type] || '').length}) */}
                        <button className='vacancies-info-button'>?</button>
                      </span>
                      <input
                        type='text'
                        placeholder='Навык'
                        value={skillInputs[type] || ''}
                        onChange={(e) => handleSkillChange(type, e.target.value)}
                        className='vacancies-filter-input' />
                    </div>
                  ))}
                </div>
              )}

              {/* Заголовок с кнопкой сворачивания */}
              {/* Раздел суммарных требований */}
              <div className="filter-section-header" onClick={toggleSummarySection}>
                <h4 className="filter-section-title">Указано в описании вакансии</h4>
                <span className="collapse-icon">
                  {isSummaryExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Содержимое секции */}
              {isSummaryExpanded && (
                <div className="filter-section-content">
                  {skillOption.map((type) => (
                    <div className='vacancies-filter-label'>
                      <span className='vacancies-filter-count'>
                        {type}
                        <button className='vacancies-info-button'>?</button>
                      </span>
                      <input
                        type='text'
                        placeholder='Требования'
                        value={summaryInputs[type] || ''}
                        onChange={(e) => handleSummaryChange(type, e.target.value)}
                        className='vacancies-filter-input' />
                    </div>
                  ))}
                </div>
              )}


              {/* Заголовок с кнопкой сворачивания */}
              {/* Раздел зарплат */}
              <div className="filter-section-header" onClick={toggleSalarySection}>
                <h4 className="filter-section-title">Зароботная плата</h4>
                <span className="collapse-icon">
                  {isSalaryExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Содержимое секции */}
              {isSalaryExpanded && (
                <div className="filter-section-content">
                  {rangeOption.map((type) => (
                    <div className='vacancies-filter-label'>
                      <span className='vacancies-filter-count'>
                        {type}
                        <button className='vacancies-info-button'>?</button>
                      </span>
                      <input
                        type='text'
                        placeholder='Зароботная плата'
                        value={summaryInputs[type] || ''}
                        onChange={(e) => handleSalaryChange(type, e.target.value)}
                        className='vacancies-filter-input' />
                    </div>
                  ))}
                </div>
              )}


              {/* Заголовок с кнопкой сворачивания */}
              {/* Раздел опыта */}
              <div className="filter-section-header" onClick={toggleExperienceSection}>
                <h4 className="filter-section-title">Опыт</h4>
                <span className="collapse-icon">
                  {isSalaryExpanded ? '▲' : '▼'}
                </span>
              </div>

              {/* Содержимое секции */}
              {isExpirienceExpanded && (
                <div className="filter-section-content">
                  {rangeOption.map((type) => (
                    <div className='vacancies-filter-label'>
                      <span className='vacancies-filter-count'>
                        {type}
                        <button className='vacancies-info-button'>?</button>
                      </span>
                      <input
                        type='text'
                        placeholder='Опыт'
                        value={summaryInputs[type] || ''}
                        onChange={(e) => handleExperienceChange(type, e.target.value)}
                        className='vacancies-filter-input' />
                    </div>
                  ))}
                </div>
              )}


            </div>

            <div className="vacancies-filter-buttons">
              <button
                onClick={() => setSkillInputs({})}
                className="vacancies-reset-button"
              >
                Сбросить фильтры
              </button>
              <button onClick={requestSearch} className="vacancies-apply-button">Применить</button>
            </div>
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
                <div key={vacancy.resume_id} className="vacancy-card">
                  <h3 className="vacancy-title">{vacancy.description}</h3>
                  <div className="vacancy-details">
                    <div className="vacancy-company-info">
                      <p className="vacancy-company">{vacancy.experience_age}</p>
                      <div className="vacancy-meta-info">
                        <span>{vacancy.location}</span>
                        <span>•</span>
                        <span>{vacancy.salary_from}</span>
                        <span>•</span>
                        <span>{vacancy.salary_to}</span>
                      </div>
                    </div>
                    <div className="vacancy-salary-container">
                      <p className="vacancy-salary">
                        {vacancy.salary_from.toLocaleString()} ₽
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
