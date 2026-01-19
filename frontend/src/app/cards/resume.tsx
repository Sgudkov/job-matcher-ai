import {ResumeDescriptionResponse} from "@/src/types/types";
import {useAuth} from "../context/AuthContext";
import React from "react";
import {useRouter} from "next/navigation";

interface ResumeCardProps {
    resumeData: ResumeDescriptionResponse | null;
}

const ResumeCard: React.FC<ResumeCardProps> = ({resumeData}) => {
    const {user, isLoading} = useAuth();
    const router = useRouter();

    const renderUserInfo = () => {
        if (!resumeData) return null;
        if (!resumeData.candidate) return null;

        return (
            <>
                <h2 className="text-2xl font-semibold mb-1">
                    {`${resumeData.candidate.first_name} ${resumeData.candidate.last_name}`}
                </h2>
                <p className="flex items-center gap-2 text-gray-200">
                    <strong>Возраст:</strong> {resumeData.candidate.age}
                </p>
                <p className="flex items-center gap-2 text-gray-200">
                    <strong>Телефон:</strong> {resumeData.candidate.phone}
                </p>
            </>
        );
    };

    const renderResumeInfo = () => {
        if (!resumeData) return null;
        if (!resumeData.resume_description) return null;
        return (
            <>
                <h3 className="text-lg font-semibold mt-6 mb-1">Описание</h3>
                <p className="text-gray-300">
                    {resumeData.resume_description.summary || "Не указано"}
                </p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Место работы</h3>
                <p className="text-gray-300">{resumeData.resume_description.location || "Не указано"}</p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Опыт работы</h3>
                <p className="text-gray-300">
                    {resumeData.resume_description.experience_age
                        ? `${resumeData.resume_description.experience_age} лет`
                        : "Не указано"}
                </p>

                <h3 className="text-lg font-semibold mt-6 mb-1">Навыки</h3>
                {resumeData.skills && resumeData.skills.length > 0 ? (
                    <ul className="mt-2">
                        {resumeData.skills.map((skill, index) => (
                            <li key={index} className="mb-4 border-b border-gray-700 pb-2">
                                <strong className="block mb-1">{skill.skill_name}</strong>
                                <p className="text-gray-300">{skill.description}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-300">Навыки не указаны</p>
                )}

                <h3 className="text-lg font-semibold mt-6 mb-1">Занятость</h3>
                {resumeData.resume_description.employment_type ? (
                    <p className="flex items-center gap-2 text-gray-300">
                        <strong>Тип занятости:</strong>

                        {resumeData.resume_description.employment_type}

                    </p>
                ) : (
                    <p className="text-gray-300"></p>
                )}


            </>
        );
    };

    return (

        <div className="bg-white flex items-center justify-center p-4">

            <div
                className="max-w-3xl w-full mt-10 bg-gradient-to-br from-gray-800 to-gray-900 p-8 rounded-2xl shadow-2xl border border-gray-700 text-white space-y-6">
                <div className="border-b border-gray-700 pb-4">
                    {/* Кнопка «Назад» */}
                    <button
                        onClick={() => router.back()}
                        className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors mb-4"
                        aria-label="Назад"
                    >
                        {/* SVG‑стрелка */}
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        <span>Назад</span>
                    </button>
                    <h1 className="text-3xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        {resumeData ? resumeData.resume_description?.title : ""}
                    </h1>
                    <br/>
                    <h1 className="text-3xl font-extrabold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                        Зарплата {resumeData?.resume_description?.salary_from} - {resumeData?.resume_description?.salary_to}
                    </h1>
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
                    {renderResumeInfo()}
                </div>
            </div>
        </div>
    );
};

export default ResumeCard;
