'use client';

import Link from 'next/link';
import { useAuth } from '../app/context/AuthContext';

export default function HomePage() {
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
            <div className="container mx-auto px-4 py-16">
                {/* Hero Section */}
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-bold text-gray-800 mb-4">
                        Добро пожаловать в Job Matcher AI
                    </h1>
                    <p className="text-xl text-gray-600 mb-8">
                        Умный подбор вакансий и резюме с помощью искусственного интеллекта
                    </p>

                    {!user && (
                        <div className="flex gap-4 justify-center">
                            <Link
                                href="/auth/login"
                                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors no-underline"
                            >
                                Войти
                            </Link>
                            <Link
                                href="/auth/register"
                                className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors no-underline"
                            >
                                Регистрация
                            </Link>
                        </div>
                    )}
                </div>

                {/* Features Section */}
                <div className="grid md:grid-cols-3 gap-8 mt-12">
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-2xl font-semibold text-gray-800 mb-3">
                            🎯 Умный поиск
                        </h3>
                        <p className="text-gray-600">
                            AI-алгоритмы для точного подбора вакансий и кандидатов
                        </p>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-2xl font-semibold text-gray-800 mb-3">
                            📊 Аналитика
                        </h3>
                        <p className="text-gray-600">
                            Детальная статистика и рекомендации для улучшения результатов
                        </p>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-2xl font-semibold text-gray-800 mb-3">
                            ⚡ Быстро и просто
                        </h3>
                        <p className="text-gray-600">
                            Интуитивный интерфейс для комфортной работы
                        </p>
                    </div>
                </div>

                {/* CTA Section */}
                {user && (
                    <div className="mt-16 text-center bg-blue-100 p-8 rounded-lg">
                        <h2 className="text-3xl font-bold text-gray-800 mb-4">
                            Привет, {user.first_name}!
                        </h2>
                        {user.role === 'candidate' ? (
                            <>
                                <p className="text-gray-700 mb-6">
                                    Найдите идеальную вакансию с помощью AI
                                </p>
                                <Link
                                    href="/vacancies"
                                    className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors no-underline inline-block"
                                >
                                    Смотреть вакансии
                                </Link>
                            </>
                        ) : (
                            <>
                                <p className="text-gray-700 mb-6">
                                    Найдите лучших кандидатов для вашей компании
                                </p>
                                <Link
                                    href="/resumes"
                                    className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors no-underline inline-block"
                                >
                                    Смотреть резюме
                                </Link>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
