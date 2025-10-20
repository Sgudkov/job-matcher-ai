'use client';

import {useAuth} from "../context/AuthContext";
import React from "react";
import {VacancyDescriptionResponse} from "../types/types";
import {useRouter} from "next/navigation";

interface VacancyCardProps {
    vacancyData: VacancyDescriptionResponse | null;
}

const VacancyCard: React.FC<VacancyCardProps> = ({vacancyData}) => {
    const {user, isLoading} = useAuth();
    const router = useRouter();

    const renderUserInfo = () => (
        <>
            <h2 className="text-2xl font-semibold mb-1">
                {`${vacancyData?.employer?.first_name} ${vacancyData?.employer?.last_name}`}
            </h2>
            <p className="flex items-center gap-2 text-gray-200">
                <strong>Телефон:</strong> {vacancyData?.employer?.phone}
            </p>
        </>
    );

    const renderVacancyInfo = () => {
        if (!vacancyData) return null;

        const {
            vacancy_description: {
                title,
                summary,
                experience_age_from,
                experience_age_to,
                location,
                salary_from,
                salary_to,
                employment_type,
                work_mode
            },
            skills
        } = vacancyData;

        return (
            <>
                <h3 className="text-lg font-semibold mt-6 mb-1">Описание</h3>
                <p className="text-gray-300">{summary || "Не указано"}</p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Опыт работы</h3>
                <p className="text-gray-300">
                    {experience_age_from} - {experience_age_to} лет
                </p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Место работы</h3>
                <p className="text-gray-300">{location || "Не указано"}</p>


                <h3 className="text-lg font-semibold mt-6 mb-1">Тип занятости</h3>
                <p className="text-gray-300">{employment_type || "Не указано"}</p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Формат работы</h3>
                <p className="text-gray-300">{work_mode || "Не указано"}</p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Навыки</h3>
                {skills && skills.length > 0 ? (
                    <ul className="mt-2">
                        {skills.map((skill, index) => (
                            <li key={index} className="mb-4 border-b border-gray-700 pb-2">
                                <strong className="block mb-1">{skill.skill_name}</strong>
                                {/*<p className="text-gray-300">{skill.description}</p>*/}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-300">Навыки не указаны</p>
                )}

            </>
        );
    };

    /* ----------  Кнопка «Назад»  ---------- */
    const goBack = () => router.back();

    return (
        <div className="bg-white flex items-center justify-center p-4">
            <div
                className="max-w-3xl w-full mt-10 bg-gradient-to-br from-gray-800 to-gray-900 p-8 rounded-2xl shadow-2xl border border-gray-700 text-white space-y-6">
                {/* Блок «Назад» */}
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        {vacancyData?.vacancy_description?.title}
                    </h1>
                    <button
                        onClick={goBack}
                        className="text-sm font-medium text-blue-300 hover:text-blue-500"
                    >
                        ← Назад
                    </button>
                </div>


                {isLoading ? (
                    <p className="text-center text-gray-400">Загрузка данных…</p>
                ) : user ? (
                    renderUserInfo()
                ) : (
                    <div className="text-red-500 text-lg text-center">
                        Пользователь не авторизован
                    </div>
                )}

                <div className="border-t border-gray-700 pt-6">
                    {renderVacancyInfo()}
                </div>
            </div>
        </div>
    );
};

export default VacancyCard;
