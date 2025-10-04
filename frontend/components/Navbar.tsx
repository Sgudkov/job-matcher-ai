'use client';

import Link from "next/link";
import { usePathname } from 'next/navigation';
import { useAuth } from '../app/context/AuthContext';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout, isLoading } = useAuth();

  const handleLogout = () => {
    logout();
  };

  // При авторизации показываем только ссылку на главную
  if (pathname.startsWith('/auth')) return (
    <div>
      <Link href="/">Главная</Link>
    </div>
  );

  if (isLoading) {
    return (
      <nav style={{ padding: '1rem', backgroundColor: '#f8f9fa' }}>
        <div>Загрузка...</div>
      </nav>
    );
  }


  return (
    <nav>
      {/* Блок авторизации */}
      <div>
        {user ?
          (
            <div>
              <span>Привет, {user.first_name} </span>
              <Link href="/profile">Профиль</Link>
              <Link href="/">Главная</Link>
              <button onClick={handleLogout}>Выход</button>
            </div>
          ) :
          (
            <div>
              <Link href="auth/login">Вход</Link>
              <Link href="auth/register">Регистрация</Link>
            </div>
          )}
      </div>
    </nav>
  );
}
