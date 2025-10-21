"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CreateVacancy() {
  const router = useRouter();

  // ---------- Vacancy state ----------
  const [employerId, setEmployerId] = useState(0);
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [experienceFrom, setExperienceFrom] = useState(0);
  const [experienceTo, setExperienceTo] = useState(0);
  const [location, setLocation] = useState('');
  const [salaryFrom, setSalaryFrom] = useState(0);
  const [salaryTo, setSalaryTo] = useState(0);
  const [employmentType, setEmploymentType] = useState('');
  const [workMode, setWorkMode] = useState('');

  // ---------- Skills state ----------
  const [skills, setSkills] = useState([
    {
      skill_name: '',
      experience_age: 0,
      description: '',
      description_hidden: '',
    },
  ]);

  // ---------- UI helpers ----------
  const addSkill = () =>
    setSkills([
      ...skills,
      { skill_name: '', experience_age: 0, description: '', description_hidden: '' },
    ]);

  const removeSkill = (index: number) =>
    setSkills(skills.filter((_, i) => i !== index));

  const updateSkill = (index: number, field: keyof typeof skills[0], value: any) => {
    const newSkills = [...skills];
    newSkills[index] = { ...newSkills[index], [field]: value };
    setSkills(newSkills);
  };

  // ---------- Submit ----------
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      vacancy: {
        employer_id: employerId,
        title,
        summary,
        experience_age_from: experienceFrom,
        experience_age_to: experienceTo,
        location,
        salary_from: salaryFrom,
        salary_to: salaryTo,
        employment_type: employmentType,
        work_mode: workMode,
        id: 0,
      },
      skills: skills.map((s) => ({
        vacancy_id: 0,
        skill_name: s.skill_name,
        experience_age: s.experience_age,
        description: s.description,
        description_hidden: s.description_hidden,
      })),
    };

    try {
      // Замените на реальный эндпоинт
      await fetch('/api/vacancies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      router.push('/vacancies');
    } catch (err) {
      console.error(err);
      alert('Ошибка при создании вакансии');
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Создать вакансию</h1>

      <form onSubmit={onSubmit} className="space-y-4">
        {/* Employer */}
        <div>
          <label className="block text-sm font-medium mb-1">Работодатель</label>
          <input
            type="number"
            value={employerId}
            onChange={(e) => setEmployerId(Number(e.target.value))}
            placeholder="ID работодателя"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium mb-1">Заголовок</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Название вакансии"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        {/* Summary */}
        <div>
          <label className="block text-sm font-medium mb-1">Краткое описание</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Кратко опишите вакансию"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        {/* Experience */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Опыт (от)</label>
            <input
              type="number"
              value={experienceFrom}
              onChange={(e) => setExperienceFrom(Number(e.target.value))}
              placeholder="0"
              className="w-full border rounded px-3 py-2 border-gray-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Опыт (до)</label>
            <input
              type="number"
              value={experienceTo}
              onChange={(e) => setExperienceTo(Number(e.target.value))}
              placeholder="0"
              className="w-full border rounded px-3 py-2 border-gray-300"
            />
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium mb-1">Местоположение</label>
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Город, регион"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        {/* Salary */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Зарплата (от)</label>
            <input
              type="number"
              value={salaryFrom}
              onChange={(e) => setSalaryFrom(Number(e.target.value))}
              placeholder="0"
              className="w-full border rounded px-3 py-2 border-gray-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Зарплата (до)</label>
            <input
              type="number"
              value={salaryTo}
              onChange={(e) => setSalaryTo(Number(e.target.value))}
              placeholder="0"
              className="w-full border rounded px-3 py-2 border-gray-300"
            />
          </div>
        </div>

        {/* Employment type */}
        <div>
          <label className="block text-sm font-medium mb-1">Тип занятости</label>
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="w-full border rounded px-3 py-2 border-gray-300"
          >
            <option value="">Выберите тип</option>
            <option value="full_time">Полная занятость</option>
            <option value="part_time">Частичная занятость</option>
            <option value="contract">Контракт</option>
            <option value="internship">Стажировка</option>
          </select>
        </div>

        {/* Work mode */}
        <div>
          <label className="block text-sm font-medium mb-1">Режим работы</label>
          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="w-full border rounded px-3 py-2 border-gray-300"
          >
            <option value="">Выберите режим</option>
            <option value="on_site">Офис</option>
            <option value="remote">Удалённо</option>
            <option value="hybrid">Гибрид</option>
          </select>
        </div>

        {/* Skills */}
        <div className="space-y-4">
          <label className="block text-sm font-medium mb-1">Навыки</label>
          {skills.map((skill, idx) => (
            <div key={idx} className="border p-4 rounded">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Навык</label>
                  <input
                    value={skill.skill_name}
                    onChange={(e) => updateSkill(idx, 'skill_name', e.target.value)}
                    placeholder="Название навыка"
                    className="w-full border rounded px-3 py-2 border-gray-300"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Опыт (лет)</label>
                  <input
                    type="number"
                    value={skill.experience_age}
                    onChange={(e) => updateSkill(idx, 'experience_age', Number(e.target.value))}
                    placeholder="0"
                    className="w-full border rounded px-3 py-2 border-gray-300"
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium mb-1">Описание</label>
                <textarea
                  value={skill.description}
                  onChange={(e) => updateSkill(idx, 'description', e.target.value)}
                  placeholder="Краткое описание навыка"
                  className="w-full border rounded px-3 py-2 border-gray-300"
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium mb-1">Скрытое описание</label>
                <textarea
                  value={skill.description_hidden}
                  onChange={(e) => updateSkill(idx, 'description_hidden', e.target.value)}
                  placeholder="Скрытое описание навыка"
                  className="w-full border rounded px-3 py-2 border-gray-300"
                />
              </div>

              <button
                type="button"
                onClick={() => removeSkill(idx)}
                className="mt-2 text-sm text-red-600 hover:underline"
              >
                Удалить
              </button>
            </div>
          ))}

          <button
            type="button"
            onClick={addSkill}
            className="w-full text-center border rounded px-3 py-2 bg-gray-100 hover:bg-gray-200"
          >
            Добавить навык
          </button>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700"
          >
            Создать вакансию
          </button>
        </div>
      </form>
    </div>
  );
}
