// app/vacancies/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { getSearchData } from '../../lib/api';
import { createSearch, FoundResume } from '../types/types';

export default function VacanciesPage() {
  const [search, setSearch] = useState('');
  const [skillInputs, setSkillInputs] = useState({});
  const [summaryInputs, setSummaryInputs] = useState({});
  const [isSkillsExpanded, setIsSkillsExpanded] = useState(true);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(true);
  const [isSalaryExpanded, setIsSalaryExpanded] = useState(true);
  const [isExperienceExpanded, setIsExperienceExpanded] = useState(true);
  const [filteredVacancies, setFilteredVacancies] = useState<FoundResume[] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const vacanciesPerPage = 10;

  // Преобразует строку в массив навыков (разделитель - запятая)
  const getSkillsArray = (skillsString: string) => {
    return skillsString
      ? skillsString
          .split(',')
          .map((skill) => skill.trim())
          .filter((skill) => skill.length > 0)
      : [];
  };

  const skillOption = ['Включить', 'Исключить'];
  const rangeOption = ['От', 'До'];

  // Получение вакансий при первом рендере
  useEffect(() => {
    const fetchData = async () => {
      const searchData = createSearch();
      searchData.filters.skills.must_have = getSkillsArray(skillInputs['Включить'] );
      searchData.filters.skills.must_not_have = getSkillsArray(skillInputs['Исключить']);
      const res = await getSearchData(searchData);
      setFilteredVacancies(res);
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const requestSearch = () => {
    const searchData = createSearch();
    searchData.filters.skills.must_have = getSkillsArray(skillInputs['Включить'] || '');
    searchData.filters.skills.must_not_have = getSkillsArray(skillInputs['Исключить'] || '');
    getSearchData(searchData).then((res) => {
      setFilteredVacancies(res);
      setCurrentPage(1);
    });
  };

  const vacanciesToShow = filteredVacancies || [];

  // Вычисляем вакансии для текущей страницы
  const indexOfLastVacancy = currentPage * vacanciesPerPage;
  const indexOfFirstVacancy = indexOfLastVacancy - vacanciesPerPage;
  const currentVacancies = vacanciesToShow.slice(indexOfFirstVacancy, indexOfLastVacancy);

  const totalPages = Math.ceil(vacanciesToShow.length / vacanciesPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="flex flex-col">
      {/* Шапка с поиском */}
      <div className="text-white p-4 flex justify-center shadow-md">
        <div className="flex items-center justify-between max-w-[1200px] w-full border-2 border-gray-300 rounded-lg p-1">
          <input
            type="text"
            placeholder="Поиск"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border-none p-2 text-base outline-none bg-transparent w-full"
          />
          <button className="bg-blue-600 text-white border-none px-4 py-2 text-base cursor-pointer rounded hover:bg-blue-700" onClick={requestSearch}>
            Найти
          </button>
        </div>
      </div>

      {/* Основной контент */}
      <div className="flex justify-start max-w-[1600px] w-full mx-auto py-5 gap-[120px] overflow-x-hidden">
        {/* Фильтры */}
        <div className="flex-[0_0_520px] min-w-[520px] max-w-[600px] w-[520px] h-screen sticky top-0 self-start">
          <div className="bg-white rounded-[14px] shadow-md p-6 pb-[88px] mb-6 border border-gray-100 relative min-h-screen">
            <h3 className="text-xl font-bold text-gray-800 mb-2 mt-0">Фильтры</h3>
            <div className="flex flex-col">
              {/* Раздел навыков */}
              <div className="flex justify-between items-center cursor-pointer py-2.5 border-b border-gray-300 mb-2 select-none text-[1.05rem] font-medium text-gray-700 hover:bg-gray-50 hover:rounded-lg transition-colors" onClick={() => setIsSkillsExpanded((v) => !v)}>
                <h4 className="m-0">Навыки</h4>
                <span>{isSkillsExpanded ? '▲' : '▼'}</span>
              </div>
              {isSkillsExpanded && (
                <div className="pb-2.5 mb-2 w-full">
                  {skillOption.map((type, idx) => (
                    <div className="flex items-center justify-between mb-2.5 gap-2.5" key={type + idx}>
                      <span className="text-base text-gray-700 font-medium flex items-center gap-1">
                        {type}
                        <button className="rounded-full text-[#4f8cff] border border-[#4f8cff] cursor-help text-xs ml-1.5 font-bold bg-gray-50 w-5 h-5 flex items-center justify-center transition-all hover:bg-[#4f8cff] hover:text-white">?</button>
                      </span>
                      <input
                        type="text"
                        placeholder="Навык"
                        value={skillInputs[type] || ''}
                        onChange={(e) => setSkillInputs((prev) => ({ ...prev, [type]: e.target.value }))}
                        className="border border-gray-300 rounded-lg text-base px-2.5 py-1.5 w-[70%] bg-gray-50 transition-colors focus:border-[#4f8cff] focus:bg-white focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Раздел суммарных требований */}
              <div className="flex justify-between items-center cursor-pointer py-2.5 border-b border-gray-300 mb-2 select-none text-[1.05rem] font-medium text-gray-700 hover:bg-gray-50 hover:rounded-lg transition-colors" onClick={() => setIsSummaryExpanded((v) => !v)}>
                <h4 className="m-0">Указано в описании вакансии</h4>
                <span>{isSummaryExpanded ? '▲' : '▼'}</span>
              </div>
              {isSummaryExpanded && (
                <div className="pb-2.5 mb-2 w-full">
                  {skillOption.map((type, idx) => (
                    <div className="flex items-center justify-between mb-2.5 gap-2.5" key={type + idx}>
                      <span className="text-base text-gray-700 font-medium flex items-center gap-1">
                        {type}
                        <button className="rounded-full text-[#4f8cff] border border-[#4f8cff] cursor-help text-xs ml-1.5 font-bold bg-gray-50 w-5 h-5 flex items-center justify-center transition-all hover:bg-[#4f8cff] hover:text-white">?</button>
                      </span>
                      <input
                        type="text"
                        placeholder="Требования"
                        value={summaryInputs[type] || ''}
                        onChange={(e) => setSummaryInputs((prev) => ({ ...prev, [type]: e.target.value }))}
                        className="border border-gray-300 rounded-lg text-base px-2.5 py-1.5 w-[70%] bg-gray-50 transition-colors focus:border-[#4f8cff] focus:bg-white focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Раздел зарплат */}
              <div className="flex justify-between items-center cursor-pointer py-2.5 border-b border-gray-300 mb-2 select-none text-[1.05rem] font-medium text-gray-700 hover:bg-gray-50 hover:rounded-lg transition-colors" onClick={() => setIsSalaryExpanded((v) => !v)}>
                <h4 className="m-0">Зароботная плата</h4>
                <span>{isSalaryExpanded ? '▲' : '▼'}</span>
              </div>
              {isSalaryExpanded && (
                <div className="pb-2.5 mb-2 w-full">
                  {rangeOption.map((type, idx) => (
                    <div className="flex items-center justify-between mb-2.5 gap-2.5" key={type + idx}>
                      <span className="text-base text-gray-700 font-medium flex items-center gap-1">
                        {type}
                        <button className="rounded-full text-[#4f8cff] border border-[#4f8cff] cursor-help text-xs ml-1.5 font-bold bg-gray-50 w-5 h-5 flex items-center justify-center transition-all hover:bg-[#4f8cff] hover:text-white">?</button>
                      </span>
                      <input
                        type="text"
                        placeholder="Зароботная плата"
                        value={summaryInputs[type] || ''}
                        onChange={(e) => setSummaryInputs((prev) => ({ ...prev, [type]: e.target.value }))}
                        className="border border-gray-300 rounded-lg text-base px-2.5 py-1.5 w-[70%] bg-gray-50 transition-colors focus:border-[#4f8cff] focus:bg-white focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Раздел опыта */}
              <div className="flex justify-between items-center cursor-pointer py-2.5 border-b border-gray-300 mb-2 select-none text-[1.05rem] font-medium text-gray-700 hover:bg-gray-50 hover:rounded-lg transition-colors" onClick={() => setIsExperienceExpanded((v) => !v)}>
                <h4 className="m-0">Опыт</h4>
                <span>{isExperienceExpanded ? '▲' : '▼'}</span>
              </div>
              {isExperienceExpanded && (
                <div className="pb-2.5 mb-2 w-full">
                  {rangeOption.map((type, idx) => (
                    <div className="flex items-center justify-between mb-2.5 gap-2.5" key={type + idx}>
                      <span className="text-base text-gray-700 font-medium flex items-center gap-1">
                        {type}
                        <button className="rounded-full text-[#4f8cff] border border-[#4f8cff] cursor-help text-xs ml-1.5 font-bold bg-gray-50 w-5 h-5 flex items-center justify-center transition-all hover:bg-[#4f8cff] hover:text-white">?</button>
                      </span>
                      <input
                        type="text"
                        placeholder="Опыт"
                        value={summaryInputs[type] || ''}
                        onChange={(e) => setSummaryInputs((prev) => ({ ...prev, [type]: e.target.value }))}
                        className="border border-gray-300 rounded-lg text-base px-2.5 py-1.5 w-[70%] bg-gray-50 transition-colors focus:border-[#4f8cff] focus:bg-white focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="flex flex-row gap-3 justify-center items-center fixed left-0 bottom-0 w-[425px] px-10 py-5 bg-white z-10 border-t border-gray-100 shadow-[0_-2px_12px_rgba(0,0,0,0.04)] rounded-b-[18px] lg:left-[calc((100vw-1600px)/2)] lg:rounded-[18px]">
            <button
              onClick={() => setSkillInputs({})}
              className="bg-[#4f8cff] text-white border-none px-4 py-2 text-base cursor-pointer rounded-lg font-medium transition-colors hover:bg-[#2357d5]"
            >
              Сбросить фильтры
            </button>
            <button onClick={requestSearch} className="bg-[#4f8cff] text-white border-none px-4 py-2 text-base cursor-pointer rounded-lg font-medium transition-colors hover:bg-[#2357d5]">
              Применить
            </button>
          </div>
        </div>

        {/* Список вакансий */}
        <div className="flex-1 w-full min-w-0 flex flex-col items-center">
          <div className="w-full max-w-[1100px] mx-auto flex flex-col items-center">
            <div className="text-lg font-semibold text-gray-700 mb-6">
              Найдено вакансий: {vacanciesToShow.length}
            </div>

            <div className="flex flex-col gap-7 w-full">
              {currentVacancies.length > 0 ? (
                currentVacancies.map((vacancy, idx) => (
                  <div key={vacancy.resume_id} className="w-full mb-2 bg-white rounded-[14px] shadow-[0_2px_12px_rgba(0,0,0,0.06)] p-8 px-14 flex flex-col items-start gap-3.5 transition-shadow border border-gray-100 hover:shadow-[0_8px_32px_rgba(0,0,0,0.12)] hover:border-gray-300">
                    <div className="text-[1.3rem] font-bold m-0 mb-1.5 text-gray-800 text-left flex-1">{vacancy.skill_name}</div>
                    <div className="text-[1.05rem] text-gray-600 m-0 mb-1 font-medium">{vacancy.description}</div>
                    <div className="flex gap-3 text-gray-500 text-base items-center flex-wrap">
                      <span>{vacancy.location}</span>
                      <span>•</span>
                      <span>{vacancy.experience_age}</span>
                      <span>•</span>
                      <span>{vacancy.location}</span>
                    </div>
                    <div className="text-[1.15rem] font-bold text-green-700 bg-green-50 rounded-lg px-5 py-2 m-0 whitespace-nowrap text-right">
                      {vacancy.salary_from
                        ? `${vacancy.salary_from.toLocaleString()} ₽`
                        : vacancy.salary_from
                        ? `${vacancy.salary_to.toLocaleString()} ₽`
                        : 'Зарплата не указана'}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <p className="text-xl font-semibold text-gray-700 mb-2">Вакансии не найдены</p>
                  <p className="text-base text-gray-500">Попробуйте изменить параметры поиска</p>
                </div>
              )}
            </div>

            {/* Пагинация */}
            {vacanciesToShow.length > 0 && (
              <div className="flex justify-center gap-2 mt-6">
                <button
                  className="bg-white border border-[#4f8cff] text-[#4f8cff] rounded-md px-3.5 py-1.5 text-base cursor-pointer transition-all hover:bg-[#4f8cff] hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Назад
                </button>
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i + 1}
                    className={`bg-white border border-[#4f8cff] rounded-md px-3.5 py-1.5 text-base cursor-pointer transition-all ${currentPage === i + 1 ? 'bg-[#4f8cff] text-white' : 'text-[#4f8cff] hover:bg-[#4f8cff] hover:text-white'}`}
                    onClick={() => handlePageChange(i + 1)}
                  >
                    {i + 1}
                  </button>
                ))}
                <button
                  className="bg-white border border-[#4f8cff] text-[#4f8cff] rounded-md px-3.5 py-1.5 text-base cursor-pointer transition-all hover:bg-[#4f8cff] hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Вперед
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
