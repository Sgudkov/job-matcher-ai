'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../app/context/AuthContext';
import { User } from '../app/context/AuthContext';

const navbarStyles = {
  backgroundColor: '#333',
  padding: '1rem',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
};

const linkStyles = {
  color: 'white',
  marginRight: '1rem',
  textDecoration: 'none',
};


export default function Navbar() {
  const pathname = usePathname();
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();


  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (pathname.startsWith('/auth')) return (
    <nav style={navbarStyles}>
      <Link href="/" style={linkStyles}>Главная</Link>
    </nav>
  );

  if (isLoading) {
    return (
      <nav style={navbarStyles}>
        <div>Загрузка...</div>
      </nav>
    );
  }


  return (
    <nav style={navbarStyles}>
      {/* Блок авторизации */}
      <div>
        {user ?
          (
            <div>
              <span style={{ color: 'white' }}>Привет, {user.first_name} </span>
              <Link href="/profile" style={linkStyles}>Профиль</Link>
              <Link href="/" style={linkStyles}>Главная</Link>
              <Link href='/vacancies' style={linkStyles}>Вакансии</Link>
              <button onClick={handleLogout} style={{ marginLeft: '1rem', backgroundColor: 'transparent', color: 'white', border: 'none', cursor: 'pointer' }}>Выход</button>
            </div>
          ) :
          (
            <div>
              <nav >
                <Link href="/auth/login" style={linkStyles}>Вход</Link>
                <Link href="/auth/register" style={linkStyles}>Регистрация</Link>
              </nav>
            </div>
          )}
      </div>
    </nav>
  );
}
