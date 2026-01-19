"use client";
import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {createResume} from "@/src/lib/api";
import PopupMessage from "@/src/components/PopupMessage";


/**
 * Типы данных, которые отправляем на бекенд
 */
type Skill = {
    resume_id: number;
    skill_name: string;
    experience_age: number;
    description: string;
};

type CandidateResume = {
    candidate_id: number;
    title: string;
    summary: string;
    experience_age: number;
    location: string;
    salary_from: number;
    salary_to: number;
    employment_type: string;
    status: 'active' | 'inactive';
    id: number;
};

type CreateResumeForm = {
    candidate_resume: CandidateResume;
    skills: Skill[];
};

export default function CreateResume() {
    const router = useRouter();
    const [message, setMessage] = useState('');

    // Локальное состояние формы
    const [form, setForm] = useState<CreateResumeForm>({
        candidate_resume: {
            candidate_id: 0,
            title: '',
            summary: '',
            experience_age: 0,
            location: '',
            salary_from: 0,
            salary_to: 0,
            employment_type: '',
            status: 'active',
            id: 0,
        },
        skills: [],
    });

    // Локальное состояние для добавления/удаления навыков
    const [skills, setSkills] = useState<Skill[]>(form.skills);

    // Обработчик изменения полей резюме
    const handleResumeChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const {name, value} = e.target;
        setForm((prev) => ({
            ...prev,
            candidate_resume: {...prev.candidate_resume, [name]: value},
        }));
    };

    // Добавление нового навыка
    const addSkill = () => {
        setSkills((prev) => [
            ...prev,
            {resume_id: 0, skill_name: '', experience_age: 0, description: ''},
        ]);
    };

    // Удаление навыка
    const removeSkill = (index: number) => {
        setSkills((prev) => prev.filter((_, i) => i !== index));
    };

    // Обновление поля навыка
    const handleSkillChange = (
        index: number,
        field: keyof Skill,
        value: string | number
    ) => {
        setSkills((prev) =>
            prev.map((s, i) => (i === index ? {...s, [field]: value} : s))
        );
    };

    // Отправка формы
    const onSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            // В реальном приложении candidate_id будет получен из контекста пользователя
            const payload = {
                ...form,
                candidate_resume: {...form.candidate_resume, candidate_id: 123},
                skills,
            };

            await createResume(payload)
            setMessage("Резюме создано успешно");
        } catch (err) {
            console.error('Ошибка при создании резюме', err);
            // TODO: показать пользователю сообщение об ошибке

        }
    };

    return (
        <div className="max-w-2xl mx-auto p-4">
            <h1 className="text-2xl font-semibold mb-4">Создать резюме</h1>

            <form onSubmit={onSubmit} className="space-y-6">
                {/* Основные данные резюме */}
                <fieldset className="border border-gray-300 p-4 rounded">
                    <legend className="text-lg font-medium">Основные данные</legend>

                    <div className="grid grid-cols-1 gap-4 mt-2">
                        <label className="block">
                            Заголовок
                            <input
                                type="text"
                                name="title"
                                value={form.candidate_resume.title}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                                required
                            />
                        </label>

                        <label className="block">
                            Местоположение
                            <input
                                type="text"
                                name="location"
                                value={form.candidate_resume.location}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                            />
                        </label>

                        <label className="block">
                            Краткое резюме
                            <textarea
                                name="summary"
                                value={form.candidate_resume.summary}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                                rows={4}
                            />
                        </label>

                        <label className="block">
                            Опыт (лет)
                            <input
                                type="number"
                                name="experience_age"
                                value={form.candidate_resume.experience_age}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                            />
                        </label>

                        <label className="block">
                            Зарплата от
                            <input
                                type="number"
                                name="salary_from"
                                value={form.candidate_resume.salary_from}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                            />
                        </label>

                        <label className="block">
                            Зарплата до
                            <input
                                type="number"
                                name="salary_to"
                                value={form.candidate_resume.salary_to}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                            />
                        </label>

                        <label className="block">
                            Тип занятости
                            <input
                                type="text"
                                name="employment_type"
                                value={form.candidate_resume.employment_type}
                                onChange={handleResumeChange}
                                className="w-full border border-gray-300 rounded p-2 mt-1"
                            />
                        </label>
                    </div>
                </fieldset>

                {/* Навыки */}
                <fieldset className="border border-gray-300 p-4 rounded">
                    <legend className="text-lg font-medium">Навыки</legend>

                    {skills.map((skill, idx) => (
                        <div
                            key={idx}
                            className="grid grid-cols-1 gap-2 mt-2 border border-gray-300 p-2 rounded"
                        >
                            <label className="block">
                                Навык
                                <input
                                    type="text"
                                    value={skill.skill_name}
                                    onChange={(e) =>
                                        handleSkillChange(idx, 'skill_name', e.target.value)
                                    }
                                    className="w-full border border-gray-300 rounded p-2 mt-1"
                                />
                            </label>

                            <label className="block">
                                Опыт (лет)
                                <input
                                    type="number"
                                    value={skill.experience_age}
                                    onChange={(e) =>
                                        handleSkillChange(idx, 'experience_age', Number(e.target.value))
                                    }
                                    className="w-full border border-gray-300 rounded p-2 mt-1"
                                />
                            </label>

                            <label className="block">
                                Описание
                                <input
                                    type="text"
                                    value={skill.description}
                                    onChange={(e) =>
                                        handleSkillChange(idx, 'description', e.target.value)
                                    }
                                    className="w-full border border-gray-300 rounded p-2 mt-1"
                                />
                            </label>

                            <button
                                type="button"
                                onClick={() => removeSkill(idx)}
                                className="text-red-600 hover:underline mt-1"
                            >
                                Удалить
                            </button>
                        </div>
                    ))}

                    <button
                        type="button"
                        onClick={addSkill}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
                    >
                        Добавить навык
                    </button>
                </fieldset>

                {/* Кнопки */}
                <div className="flex justify-end gap-4">
                    <button
                        type="button"
                        onClick={() => router.back()}
                        className="px-4 py-2 border rounded"
                    >
                        Отмена
                    </button>
                    <button
                        type="submit"
                        className="px-4 py-2 bg-green-600 text-white rounded"
                    >
                        Создать
                    </button>
                </div>
            </form>
            {/* Рендерим PopupMessage, если есть сообщение */}
            {message && <PopupMessage message={message} onClose={() => setMessage('')} />}
        </div>
    );
}
