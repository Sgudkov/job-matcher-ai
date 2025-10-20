'use client';

import {getResume, getVacancy} from "../../../lib/api";
import {useEffect, useState} from "react";
import {FoundResume, ResumeDescriptionResponse} from "../../types/types";
import {useAuth} from "../../context/AuthContext";
import {useRouter, useSearchParams} from "next/navigation";
import ResumeCard from "../resume";
import VacancyCard from "../vacancy";

export default function Card({params}: { params: { id: string } }) {
    const [resumeData, setResumeData] = useState<ResumeDescriptionResponse | null>(null);
    const [vacancyData, setVacancyData] = useState<any | null>(null);
    const [isVacancy, setIsVacancy] = useState<boolean | null>(null);
    const {user, isLoading} = useAuth();
    const searchParams = useSearchParams();
    const {id} = params;
    const router = useRouter();

    // Инициализация isVacancy на основе параметров URL
    useEffect(() => {
        const paramIsVacancy = searchParams.get('isVacancy') === 'true';
        setIsVacancy(paramIsVacancy);
    }, [searchParams]);

    // Загрузка данных в зависимости от isVacancy
    useEffect(() => {
        const fetchData = async () => {
            try {
                if (isVacancy) {
                    const vacancy = await getVacancy(Number(id));
                    setVacancyData(vacancy);
                } else {
                    const resume = await getResume(Number(id));

                    setResumeData(resume);
                }
            } catch (error) {
                console.error(isVacancy ? "Ошибка при загрузке вакансии:" : "Ошибка при загрузке резюме:", error);
            }
        };
        if (isVacancy !== null) {
            fetchData();
        }
    }, [id, isVacancy]);

    // Проверка авторизации
    useEffect(() => {
        if (!isLoading && !user) {
            console.warn("Пользователь не авторизован или данные не загружены");
        } else if (user) {
            console.log("Данные пользователя загружены:", user);
        }
    }, [isLoading, user]);


    return (
        <div className="bg-white flex items-center justify-center p-4 ">
            <div className="w-full max-w-2xl">
                {isVacancy ? <VacancyCard vacancyData={vacancyData} /> : <ResumeCard resumeData={resumeData} />}
            </div>
        </div>
    );
}
