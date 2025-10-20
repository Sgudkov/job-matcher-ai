import {NextResponse} from 'next/server';
import type {NextRequest} from 'next/server';
import {validateToken} from "./lib/api";


/**
 * Список публичных маршрутов, которые не требуют авторизации.
 */
const PUBLIC_PATHS = [
    '/auth/login',
    '/auth/register',
    '/auth/unauthorized',
    '/favicon.ico',
    '/_next/', // статические файлы Next.js
    '/',
];

const PUBLIC_PREFIXES = ['/._next/', '/_next/', '/_next/static/'];

/**
 * Путь к странице не‑авторизованного пользователя
 */
const unauthorizedPath = '/auth/unauthorized';

/**
 * Проверка, является ли путь публичным.
 */
const isPublic = (pathname: string) => {
    if (PUBLIC_PATHS.includes(pathname)) return true;

    return PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix));
};

export async function middleware(request: NextRequest) {
    const {pathname} = request.nextUrl;

    // Если путь публичный – ничего не делаем
    if (isPublic(pathname)) {
        return NextResponse.next();
    }

    // Получим токен
    const tokenCookie = request.cookies.get('token');
    const token = tokenCookie?.value;
    if (!token) {
        const url = request.nextUrl.clone();
        url.pathname = '/auth/unauthorized';
        return NextResponse.redirect(url);
    }


    // Проверим токен
    let isValid: boolean;
    try {
        isValid = await validateToken(token);
    } catch (err) {
        // Любая ошибка при проверке → считаем токен недействительным
        console.warn('Token validation error:', err);
        isValid = false;
    }

    if (!isValid) {
        const url = request.nextUrl.clone();
        url.pathname = unauthorizedPath;
        return NextResponse.redirect(url);
    }

    return NextResponse.next();
}

// Указываем Edge runtime (по умолчанию, но явно полезно)
export const config = {
    runtime: 'experimental-edge',
};
