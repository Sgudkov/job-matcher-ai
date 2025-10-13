'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

//Типы
export type UserRole = 'candidate' | 'employer';

export interface User {
    id: number;
    username: string;
    first_name: string | null;
    last_name: string | null;
    email: string | null;
    age: number | null;
    phone: string | null;
    role: UserRole;  // Роль пользователя: кандидат или работодатель
}

interface AuthContextType {
    user: User | null;
    login: (token: string, userData: User) => void;
    logout: () => void;
    isLoading: boolean;
}

//Создаем контекст
const AuthContext = createContext<AuthContextType | undefined>(undefined);

//Компонент провайдера
export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    //При загрузке приложения проверяем есть ли токен в localStorage
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            //Обновляем данные пользователя
            updateUser(token);
        }
        const userData = localStorage.getItem('user');
        if (userData) {
            setUser(JSON.parse(userData));
        }
        setIsLoading(false);
    }, []);

    useEffect(() => {
        console.log('User обновился:', user);

        if (user) {
            console.log('ID:', user.id);
            console.log('Username:', user.username);
            console.log('Email:', user.email);
        } else {
            console.log('User стал null (разлогинились)');
        }
    }, [user]);

    //Функци входа
    function login(token: string, userData: User) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
    }

    //Функци выхода
    function logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
    }

    function updateUser(token: string) {
        const userData = decodeToken(token);
        if (!userData) return;

        setUser(userData);

    }

    //Функци декодирования токена
    function decodeToken(token: string): User | null {
        try {
            const decodedToken = JSON.parse(atob(token.split('.')[1]));
            return decodedToken;
        } catch (error) {
            return null;
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
