'use client';

import React, {createContext, useContext, useState, useEffect, ReactNode, useRef} from "react";
import {validateToken} from "@/src/lib/api";
import {useRouter, usePathname} from "next/navigation";
// Типы
export type UserRole = 'candidate' | 'employer';

export interface User {
    company_name?: string;
    id: number;
    username: string;
    first_name: string | null;
    last_name: string | null;
    email: string | null;  // Email может быть получен из токена
    age: number | null;
    phone: string | null;
    role: UserRole;
}


interface AuthContextType {
    user: User | null;
    login: (token: string, userData: User) => void;
    logout: () => void;
    isLoading: boolean;
}

// Создаем контекст
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({children}: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter(); // Инициализируем роутер
    const pathname = usePathname()

    // Используем useRef для создания broadcast channel, чтобы он не пересоздавался при каждом рендере
    // и чтобы его можно было безопасно закрыть при размонтировании.
    const authChannelRef = useRef<BroadcastChannel | null>(null);

    // Инициализация канала
    if (!authChannelRef.current) {
        authChannelRef.current = new BroadcastChannel('auth_channel');
    }
    const authChannel = authChannelRef.current;

    // --- Эффект для инициализации и обработки сообщений ---
    useEffect(() => {
        const handleMessage = (event: MessageEvent) => {
            if (event.data) {
                switch (event.data.type) {
                    case 'LOGOUT':
                        console.log('Received LOGOUT message. Performing logout...');
                        // Выполняем выход, синхронизируя состояние
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        setUser(null);
                        // Перенаправляем, если пользователь не на странице входа
                        if (pathname != '/auth/login'){
                            router.push('/');
                        }
                        break;
                    case 'LOGIN_SUCCESS':
                        console.log('Received LOGIN_SUCCESS message. Updating user data...');
                        // Обновляем данные пользователя, если пришли
                        if (event.data.userData) {
                            setUser(event.data.userData);
                            localStorage.setItem('user', JSON.stringify(event.data.userData));
                        }
                        break;
                    default:
                        break;
                }
            }
        };

        // Слушаем сообщения
        authChannel.addEventListener('message', handleMessage);

        // --- Инициализация аутентификации ---
        const token = localStorage.getItem('token');

        async function initAuth() {
            if (token) {
                try {
                    // Проверяем валидность токена
                    const isValid = await validateToken(token);
                    if (isValid) {
                        updateUser(); // Загружаем данные пользователя из localStorage
                    } else {
                        // Токен невалиден
                        console.log("Invalid token found. Logging out.");
                        logout(); // Очищаем все и отправляем LOGOUT всем
                    }
                } catch (error) {
                    console.error("Error validating token:", error);
                    logout(); // Очищаем в случае ошибки валидации
                }
            }
            setIsLoading(false);
        }

        initAuth();
        return () => {
            console.log('Cleaning up AuthContext listeners and closing channel.');
            authChannel.removeEventListener('message', handleMessage);
            // Не закрываем канал здесь, если компонент будет пересоздаваться (например, при навигации)
            // Лучше закрыть его при размонтировании всего приложения (например, в корневом layout)
            // authChannel.close(); // Раскомментируйте, если уверены, что это нужно здесь
        };
    }, [router]); // Добавляем router в зависимости, если используем его внутри эффекта

    // --- Эффект для отслеживания user и перенаправления ---
    // Этот эффект будет срабатывать, когда user меняется
    useEffect(() => {
        // Если user стал null (после logout или при ошибке инициализации)
        // И мы не находимся в состоянии загрузки (т.е. это не начальная загрузка)
        if (user === null && !isLoading) {
            console.log("User is null, redirecting to login page...");
            // Перенаправляем на страницу входа, если мы еще не там
            if (pathname != "/auth/login"){
                // router.push('/auth/login');
            }
        }
        // Логирование для отладки
        console.log('User state updated:', user);
    }, [user, isLoading, router]);


    // --- Функции ---

    function login(token: string, userData: User) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        // Отправляем сообщение другим вкладкам, что произошел вход
        authChannel.postMessage({type: 'LOGIN_SUCCESS', userData: userData});
    }

    function logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        // Очистка cookie, если они используются
        document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        localStorage.removeItem('filteredVacancies');
        localStorage.removeItem('filteredResumes');

        // Отправляем сообщение всем другим вкладкам
        authChannel.postMessage({type: 'LOGOUT'});
    }

    function updateUser() {
        const userData = localStorage.getItem('user');
        if (userData) {
            setUser(JSON.parse(userData));
        }
    }

    const value = {
        user,
        login,
        logout,
        isLoading,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Hook для использования контекста
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within a AuthProvider');
    }
    return context;
}
