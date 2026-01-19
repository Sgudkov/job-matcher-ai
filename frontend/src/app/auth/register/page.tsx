"use client";

import {useState} from "react";
import {useRouter} from "next/navigation";
import Link from "next/link";
import {register, RegisterData, login} from "@/src/lib/api";
import {useAuth} from "../../context/AuthContext";

type UserRole = 'candidate' | 'employer';

export default function RegisterPage() {
    const router = useRouter();
    const {login: authLogin} = useAuth();
    const [role, setRole] = useState<UserRole>('candidate');
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [age, setAge] = useState("");
    const [phone, setPhone] = useState("");
    const [companyName, setCompanyName] = useState("");
    const [message, setMessage] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setIsLoading(true);
        setMessage("");

        try {
            const baseData = {
                role,
                email,
                password,
                first_name: firstName,
                last_name: lastName,
                phone: parseInt(phone),
            };

            const registerData: RegisterData = role === 'candidate'
                ? {...baseData, role: 'candidate', age: parseInt(age)}
                : {...baseData, role: 'employer', company_name: companyName};

            // Регистрация
            const registerRes = await register(registerData);

            // Проверяем успешность регистрации
            const isRegistrationSuccessful = registerRes && (
                registerRes.id ||
                registerRes.user_id ||
                registerRes.employer_id ||
                registerRes.candidate_id ||
                (registerRes.message && registerRes.message.includes('success'))
            );

            if (isRegistrationSuccessful) {
                setMessage("Регистрация успешна! Выполняется вход...");

                // Автоматический вход после успешной регистрации
                try {
                    const loginRes = await login(email, password);

                    if (loginRes.access_token) {
                        // Получаем данные пользователя из ответа регистрации
                        const userData = {
                            id: registerRes.id || registerRes.user_id || registerRes.employer_id || registerRes.candidate_id,
                            username: email,
                            first_name: firstName,
                            last_name: lastName,
                            email: email,
                            age: role === 'candidate' ? parseInt(age) : null,
                            phone: phone,
                            role: role
                        };

                        // Сохраняем пользователя в контексте
                        authLogin(loginRes.access_token, userData);

                        setMessage("Вход выполнен! Перенаправление...");
                        setTimeout(() => router.push('/'), 1000);
                    } else {
                        setMessage("Регистрация успешна, но не удалось выполнить вход. Пожалуйста, войдите вручную.");
                        setTimeout(() => router.push('/auth/login'), 2000);
                    }
                } catch (loginError) {
                    setMessage("Регистрация успешна, но не удалось выполнить вход. Пожалуйста, войдите вручную.");
                    setTimeout(() => router.push('/auth/login'), 2000);
                }
            } else {
                setMessage(registerRes?.detail || registerRes?.message || "Ошибка регистрации");
            }
        } catch (error) {
            setMessage("Произошла ошибка при регистрации");
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
                <h2 className="text-3xl font-bold text-gray-800 mb-2 text-center">Регистрация</h2>
                <p className="text-gray-600 mb-6 text-center">Создайте новый аккаунт</p>

                {/* Переключатель роли */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-3">Тип профиля</label>
                    <div className="grid grid-cols-2 gap-3">
                        <button
                            type="button"
                            onClick={() => setRole('candidate')}
                            className={`py-3 px-4 rounded-lg font-medium transition-all ${
                                role === 'candidate'
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            👤 Кандидат
                        </button>
                        <button
                            type="button"
                            onClick={() => setRole('employer')}
                            className={`py-3 px-4 rounded-lg font-medium transition-all ${
                                role === 'employer'
                                    ? 'bg-green-600 text-white shadow-md'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            🏢 Работодатель
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Общие поля */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                            placeholder="your@email.com"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                            placeholder="••••••••"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                            <input
                                type="text"
                                required
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                                placeholder="Иван"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                            <input
                                type="text"
                                required
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                                placeholder="Иванов"
                            />
                        </div>
                    </div>

                    {/* Поля для кандидата */}
                    {role === 'candidate' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Возраст</label>
                            <input
                                type="number"
                                required
                                value={age}
                                onChange={(e) => setAge(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                                placeholder="25"
                                min="18"
                                max="100"
                            />
                        </div>
                    )}

                    {/* Поля для работодателя */}
                    {role === 'employer' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Название компании</label>
                            <input
                                type="text"
                                required
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                                placeholder="ООО Компания"
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
                        <input
                            type="tel"
                            required
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                            placeholder="79001234567"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className={`w-full py-3 rounded-lg font-medium text-white transition-all ${
                            role === 'candidate'
                                ? 'bg-blue-600 hover:bg-blue-700'
                                : 'bg-green-600 hover:bg-green-700'
                        } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                    </button>
                </form>

                {message && (
                    <div className={`mt-4 p-3 rounded-lg text-center ${
                        message.includes('успешна') || message.includes('Вход выполнен') || message.includes('Перенаправление')
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                    }`}>
                        {message}
                    </div>
                )}

                <p className="mt-6 text-center text-gray-600">
                    Уже есть аккаунт?{' '}
                    <Link href="/auth/login" className="text-blue-600 hover:text-blue-700 font-medium">
                        Войти
                    </Link>
                </p>
            </div>
        </div>
    );
}
