"use client";
import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {createVacancy} from "@/src/lib/api";
import PopupMessage from "@/src/components/PopupMessage";

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
    const [message, setMessage] = useState('');

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
            {skill_name: '', experience_age: 0, description: '', description_hidden: ''},
        ]);

    const removeSkill = (index: number) =>
        setSkills(skills.filter((_, i) => i !== index));

    const updateSkill = (index: number, field: keyof typeof skills[0], value: any) => {
        const newSkills = [...skills];
        newSkills[index] = {...newSkills[index], [field]: value};
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

            await createVacancy(payload)
            setMessage("Резюме создано успешно");
        } catch (err) {
            console.error(err);
            alert('Ошибка при создании вакансии');
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-md space-y-8">
            <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">Создать вакансию</h1>

            <form onSubmit={onSubmit} className="space-y-6">
                {/* Employer - uncommented as it was commented out in the original file */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Работодатель</label>
                    <input
                        type="number"
                        value={employerId}
                        onChange={(e) => setEmployerId(Number(e.target.value))}
                        placeholder="ID работодателя"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                    />
                </div>

                {/* Title */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Заголовок</label>
                    <input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Название вакансии"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                    />
                </div>

                {/* Summary */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Краткое описание</label>
                    <textarea
                        value={summary}
                        onChange={(e) => setSummary(e.target.value)}
                        placeholder="Кратко опишите вакансию"
                        rows={4}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                    />
                </div>

                {/* Experience */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-lg font-semibold text-gray-700 mb-2">Опыт (от)</label>
                        <input
                            type="number"
                            value={experienceFrom}
                            onChange={(e) => setExperienceFrom(Number(e.target.value))}
                            placeholder="Минимум лет опыта"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-lg font-semibold text-gray-700 mb-2">Опыт (до)</label>
                        <input
                            type="number"
                            value={experienceTo}
                            onChange={(e) => setExperienceTo(Number(e.target.value))}
                            placeholder="Максимум лет опыта"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                        />
                    </div>
                </div>

                {/* Location */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Местоположение</label>
                    <input
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="Город, регион или удаленно"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                    />
                </div>

                {/* Salary */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-lg font-semibold text-gray-700 mb-2">Зарплата (от)</label>
                        <input
                            type="number"
                            value={salaryFrom}
                            onChange={(e) => setSalaryFrom(Number(e.target.value))}
                            placeholder="Минимальная зарплата"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-lg font-semibold text-gray-700 mb-2">Зарплата (до)</label>
                        <input
                            type="number"
                            value={salaryTo}
                            onChange={(e) => setSalaryTo(Number(e.target.value))}
                            placeholder="Максимальная зарплата"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm"
                        />
                    </div>
                </div>

                {/* Employment type */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Тип занятости</label>
                    <select
                        value={employmentType}
                        onChange={(e) => setEmploymentType(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm appearance-none"
                    >
                        <option value="">Выберите тип занятости</option>
                        <option value="full_time">Полная занятость</option>
                        <option value="part_time">Частичная занятость</option>
                        <option value="contract">Контракт</option>
                        <option value="internship">Стажировка</option>
                    </select>
                </div>

                {/* Work mode */}
                <div>
                    <label className="block text-lg font-semibold text-gray-700 mb-2">Режим работы</label>
                    <select
                        value={workMode}
                        onChange={(e) => setWorkMode(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 shadow-sm appearance-none"
                    >
                        <option value="">Выберите режим работы</option>
                        <option value="on_site">Офис</option>
                        <option value="remote">Удалённо</option>
                        <option value="hybrid">Гибрид</option>
                    </select>
                </div>

                {/* Skills */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-bold text-gray-800">Требуемые навыки</h2>
                    {skills.map((skill, idx) => (
                        <div key={idx} className="border border-gray-300 p-6 rounded-lg bg-gray-50 shadow-inner">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                                <div>
                                    <label className="block text-md font-semibold text-gray-700 mb-2">Название навыка</label>
                                    <input
                                        value={skill.skill_name}
                                        onChange={(e) => updateSkill(idx, 'skill_name', e.target.value)}
                                        placeholder="Например: Python"
                                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-indigo-400 focus:border-indigo-400"
                                    />
                                </div>

                                <div>
                                    <label className="block text-md font-semibold text-gray-700 mb-2">Опыт (лет)</label>
                                    <input
                                        type="number"
                                        value={skill.experience_age}
                                        onChange={(e) => updateSkill(idx, 'experience_age', Number(e.target.value))}
                                        placeholder="Например: 3"
                                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-indigo-400 focus:border-indigo-400"
                                    />
                                </div>
                            </div>

                            <div className="mt-4">
                                <label className="block text-md font-semibold text-gray-700 mb-2">Описание навыка</label>
                                <textarea
                                    value={skill.description}
                                    onChange={(e) => updateSkill(idx, 'description', e.target.value)}
                                    placeholder="Кратко опишите, что должен уметь кандидат"
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-indigo-400 focus:border-indigo-400"
                                />
                            </div>

                            <div className="mt-4">
                                <label className="block text-md font-semibold text-gray-700 mb-2">Скрытое описание (для внутренних заметок)</label>
                                <textarea
                                    value={skill.description_hidden}
                                    onChange={(e) => updateSkill(idx, 'description_hidden', e.target.value)}
                                    placeholder="Дополнительная информация, невидимая кандидату"
                                    rows={2}
                                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-indigo-400 focus:border-indigo-400"
                                />
                            </div>

                            <div className="flex justify-end mt-4">
                                <button
                                    type="button"
                                    onClick={() => removeSkill(idx)}
                                    className="text-sm font-medium text-red-600 hover:text-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                                >
                                    Удалить навык
                                </button>
                            </div>
                        </div>
                    ))}

                    <button
                        type="button"
                        onClick={addSkill}
                        className="w-full py-3 border-2 border-dashed border-indigo-300 rounded-lg text-indigo-600 font-semibold hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                        + Добавить еще один навык
                    </button>
                </div>

                {/* Submit */}
                <div className="flex justify-end pt-6">
                    <button
                        type="submit"
                        className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-300"
                    >
                        Создать вакансию
                    </button>
                </div>
            </form>
            {/* Рендерим PopupMessage, если есть сообщение */}
            {message && <PopupMessage message={message} onClose={() => setMessage('')} />}
        </div>
    );
}
