'use client';

import Link from 'next/link';
import {useEffect} from 'react';
import {useAuth} from "../../context/AuthContext";
import {useRouter} from 'next/navigation';

export default function UnauthorizedPage() {
    const {user, isLoading} = useAuth();
    const router = useRouter();

    // Если пользователь всё же авторизовался, перенаправляем его на главную
    useEffect(() => {
        if (!isLoading && user) {
            router.replace('/');
        }
    }, [isLoading, user, router]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md text-center">
                <h1 className="text-2xl font-semibold mb-4">Необходима авторизация</h1>
                <p className="mb-6 text-gray-600">
                    Для доступа к этой странице вам необходимо войти в систему или зарегистрироваться.
                </p>
                <div className="flex flex-col space-y-3">
                    <Link href="/auth/login"
                          className="block py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                    >
                        Войти
                    </Link>
                    <Link href="/auth/register"
                          className="block py-2 px-4 border border-blue-600 text-blue-600 rounded hover:bg-blue-50 transition"
                    >
                        Зарегистрироваться
                    </Link>
                </div>
            </div>
        </div>
    );
}
