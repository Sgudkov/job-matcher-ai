import {Search} from "../app/types/types";

const API_URL = "http://localhost:8000/api/v1";


interface Token {
    sub: number,
    role: 'candidate' | 'employer',  // Роль пользователя из токена
    email: string,  // Email пользователя из токена
    access_token: string,
    token_type: string,
    expires_in: number
}


// Интерфейсы для регистрации
interface CandidateRegisterData {
    role: 'candidate';
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    age: number;
    phone: number;
}

interface EmployerRegisterData {
    role: 'employer';
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    company_name: string;
    phone: number;
}

export type RegisterData = CandidateRegisterData | EmployerRegisterData;

export async function register(data: RegisterData) {
    const endpoint = data.role === 'candidate'
        ? `${API_URL}/auth/register/candidate/`
        : `${API_URL}/auth/register/employer/`;

    const res = await fetch(endpoint, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
    });
    return res.json();
}


export async function login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch(`${API_URL}/auth/token`, {
        method: "POST",
        // headers: { "Content-Type": "application/json" },
        body: formData,
    });
    const data = await res.json();
    if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        const cookieValue = encodeURIComponent(data.access_token);
        document.cookie = `token=${cookieValue}; path=/; max-age=${60 * 60 * 24 * 7}`;
    }
    return data;
}

export async function fetchUser(token: string) {
    const tokenData = decodeToken(token);
    if (!tokenData) {
        throw new Error('Invalid token');
    }

    // Определяем endpoint на основе роли из токена
    const endpoint = tokenData.role === 'candidate'
        ? `${API_URL}/candidates/`
        : `${API_URL}/employers/`;

    const res = await fetch(endpoint, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
    });
    const data = await res.json();

    // Добавляем роль и email из токена в данные пользователя
    return {...data, role: tokenData.role, email: tokenData.email};
}


function decodeToken(token: string): Token | null {
    try {
        const decodedToken = JSON.parse(atob(token.split('.')[1]));
        return decodedToken;
    } catch (error) {
        return null;
    }
}


export async function getSearchVacancy(searchParams: Search) {
    const res = await fetch(`${API_URL}/vacancies/search`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(searchParams),
    });
    const data = await res.json();
    return data;
}

export async function getSearchResume(searchParams: Search) {
    const res = await fetch(`${API_URL}/resumes/search`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(searchParams),
    });
    const data = await res.json();
    return data;
}


export async function getResume(id_: number) {
    const token = localStorage.getItem("token");
    if (!token) return null;
    const res = await fetch(`${API_URL}/resumes/${id_}`, {
        // method: "GET",
        headers: {Authorization: `Bearer ${token}`},
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();

}

export async function getVacancy(id_: number) {
    const token = localStorage.getItem("token");
    if (!token) return null;
    const res = await fetch(`${API_URL}/vacancies/${id_}`, {
        // method: "GET",
        headers: {Authorization: `Bearer ${token}`},
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Error ${res.status}`);
    return await res.json();
}


export async function validateToken(token?: string): Promise<boolean> {
    // Если токен не передан – берём из localStorage
    const authToken = token ?? localStorage.getItem('token');
    if (!authToken) return false;

    try {
        const res = await fetch(`${API_URL}/auth/verify-token/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authToken}`,
            },
        });

        // Если статус 200 – токен валиден
        if (res.ok) {
            // Можно дополнительно проверить тело ответа, если бекенд возвращает данные
            return true;
        }

        // Любой другой статус – токен недействителен
        return false;
    } catch (err) {
        console.error('Ошибка при проверке токена:', err);
        return false;
    }
}
