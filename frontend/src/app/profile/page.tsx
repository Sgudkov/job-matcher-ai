"use client";

import {useEffect, useState} from "react";
import {useRouter} from "next/navigation";
import {useAuth} from "@/src/app/context/AuthContext";
import Link from "next/link";

export default function ProfilePage() {
    const router = useRouter();
    const {user, logout, isLoading} = useAuth();
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (!isLoading && !user) {
            router.push('/auth/login');
        }
    }, [user, isLoading, router]);

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
                <div className="text-xl text-gray-600">Загрузка...</div>
            </div>
        );
    }

    if (!user) {
        return null;
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-8 px-4">
            <div className="max-w-4xl mx-auto">
                {/* Заголовок */}
                <div className="mb-6">
                    <Link href="/" className="text-blue-600 hover:text-blue-700 flex items-center gap-2 mb-4">
                        ← Вернуться на главную
                    </Link>
                    <h1 className="text-3xl font-bold text-gray-800">Мой профиль</h1>
                </div>

                {/* Карточка профиля */}
                <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                    {/* Шапка профиля */}
                    <div
                        className={`p-6 ${user.role === 'candidate' ? 'bg-gradient-to-r from-blue-500 to-blue-600' : 'bg-gradient-to-r from-green-500 to-green-600'}`}>
                        <div className="flex items-center gap-4">
                            <div
                                className="w-20 h-20 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-gray-700">
                                {user.first_name?.[0]}{user.last_name?.[0]}
                            </div>
                            <div className="flex-1">
                                <h2 className="text-2xl font-bold text-white">
                                    {user.first_name} {user.last_name}
                                </h2>
                                <p className="text-white/90 flex items-center gap-2">
                                    {user.role === 'candidate' ? '👤 Кандидат' : '🏢 Работодатель'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Основная информация */}
                    <div className="p-6 space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Имя */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-500">Имя</label>
                                <div className="flex items-center gap-2 text-gray-800">
                                    <span className="text-lg">👤</span>
                                    <span className="text-lg">{user.first_name || 'Не указано'}</span>
                                </div>
                            </div>

                            {/* Фамилия */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-500">Фамилия</label>
                                <div className="flex items-center gap-2 text-gray-800">
                                    <span className="text-lg">👤</span>
                                    <span className="text-lg">{user.last_name || 'Не указана'}</span>
                                </div>
                            </div>

                            {/* Название компании (только для работодателей) */}
                            {user.role === 'employer' && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-500">Название компании</label>
                                    <div className="flex items-center gap-2 text-gray-800">
                                        <span className="text-lg">🏢</span>
                                        <span className="text-lg">{user.company_name || 'Не указано'}</span>
                                    </div>
                                </div>
                            )}

                            {/* Email */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-500">Email</label>
                                <div className="flex items-center gap-2 text-gray-800">
                                    <span className="text-lg">📧</span>
                                    <span className="text-lg">{user.email || 'Не указан'}</span>
                                </div>
                            </div>

                            {/* Телефон */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-500">Телефон</label>
                                <div className="flex items-center gap-2 text-gray-800">
                                    <span className="text-lg">📱</span>
                                    <span className="text-lg">{user.phone || 'Не указан'}</span>
                                </div>
                            </div>

                            {/* Возраст (только для кандидатов) */}
                            {user.role === 'candidate' && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-gray-500">Возраст</label>
                                    <div className="flex items-center gap-2 text-gray-800">
                                        <span className="text-lg">🎂</span>
                                        <span className="text-lg">{user.age ? `${user.age} лет` : 'Не указан'}</span>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Разделитель */}
                        <div className="border-t border-gray-200 pt-6">
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">Быстрые действия</h3>
                            <div className="flex flex-wrap gap-3">
                                {user.role === 'candidate' ? (
                                    <Link
                                        href="/vacancies"
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors no-underline font-medium"
                                    >
                                        Смотреть вакансии
                                    </Link>
                                ) : (
                                    <Link
                                        href="/resumes"
                                        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors no-underline font-medium"
                                    >
                                        Смотреть резюме
                                    </Link>
                                )}

                                {/* Создание */}
                                <Link
                                    href="/create"
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors no-underline font-medium"
                                >
                                    {user.role === 'candidate' ? 'Создать резюме' : 'Создать вакансию'}
                                </Link>


                                <button
                                    onClick={handleLogout}
                                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
                                >
                                    Выйти из аккаунта
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Дополнительная информация */}
                <div className="mt-6 bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Статистика</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                        {user.role === 'candidate' ? (
                            <Link
                                href="/resumes"
                                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors no-underline font-medium"
                            >
                                Мои резюме
                            </Link>
                        ) : (
                            <Link
                                href="/vacancies"
                                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors no-underline font-medium"
                            >
                                Мои вакансии
                            </Link>
                        )}
                        <div className="bg-blue-50 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-blue-600">0</div>
                            <div className="text-sm text-gray-600 mt-1">
                                {user.role === 'candidate' ? 'Откликов' : 'Активных вакансий'}
                            </div>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-green-600">0</div>
                            <div className="text-sm text-gray-600 mt-1">
                                {user.role === 'candidate' ? 'Просмотров профиля' : 'Просмотров вакансий'}
                            </div>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4 text-center">
                            <div className="text-3xl font-bold text-purple-600">0</div>
                            <div className="text-sm text-gray-600 mt-1">Сохраненных</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
