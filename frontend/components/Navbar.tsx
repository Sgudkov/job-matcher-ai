'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../app/context/AuthContext';
import { User } from '../app/context/AuthContext';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (pathname.startsWith('/auth')) return (
    <nav className="bg-gray-800 p-4 flex justify-between items-center shadow-md">
      <Link href="/" className="text-white mr-4 no-underline hover:text-gray-300 transition-colors">Главная</Link>
    </nav>
  );

  if (isLoading) {
    return (
      <nav className="bg-gray-800 p-4 flex justify-between items-center shadow-md">
        <div className="text-white">Загрузка...</div>
      </nav>
    );
  }

  return (
    <nav className="bg-gray-800 p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        {/* Левая часть - Логотип и основные ссылки */}
        <div className="flex items-center gap-6">
          <Link href="/" className="text-white text-xl font-bold no-underline hover:text-blue-400 transition-colors">
            IdealMatch.dev
          </Link>

          {user && (
            <div className="flex items-center gap-4">
              {/* Для работодателей показываем резюме */}
              {user.role === 'employer' && (
                <Link href='/resumes' className="text-white no-underline hover:text-blue-400 transition-colors">
                  Резюме кандидатов
                </Link>
              )}

              {/* Для кандидатов показываем вакансии */}
              {user.role === 'candidate' && (
                <Link href='/vacancies' className="text-white no-underline hover:text-blue-400 transition-colors">
                  Вакансии
                </Link>
              )}
            </div>
          )}
        </div>

        {/* Правая часть - Пользователь и авторизация */}
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <span className="text-gray-300">Привет, {user.first_name}</span>
              <Link href="/profile" className="text-white no-underline hover:text-blue-400 transition-colors">
                Профиль
              </Link>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition-colors border-none cursor-pointer"
              >
                Выход
              </button>
            </>
          ) : (
            <>
              <Link
                href="/auth/login"
                className="text-white no-underline hover:text-blue-400 transition-colors"
              >
                Вход
              </Link>
              <Link
                href="/auth/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors no-underline"
              >
                Регистрация
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
