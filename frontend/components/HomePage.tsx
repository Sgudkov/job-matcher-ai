'use client';

import { useAuth } from "../app/context/AuthContext";

export default function HomePage() {
    const { user } = useAuth();
    return (
        <div style={{ padding: '50px', textAlign: 'center', backgroundImage: 'url("https://images.unsplash.com/photo-1556742212-857472f5-5fb967448c1d?ixlib=rb-1.2.1&ixid=eyJhcHBifZXRlP29yZGl0aW50b3NvcmVlZXNwb25hdXNlcml0ZV1c2VyMjUyOXclZw52RGJzdGF0aW9uMS4wJXVkdVJpZ2h0JVN1amU1cFlTYmRQbGJhZmZpbGFnZV9yWVQaGNvbmVyb3NlbnNpcmZ6aHRtbGVhZGllbnNlbnNvbnRleHR1cHM=")' }}>
            {user ?
                (
                    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
                        <h1>Добро пожаловать на страницу <span>{user.first_name}</span> <span>{user.last_name}</span></h1>
                        <p>Вот наша страница, где вы можете узнать больше о нашем приложении.</p>
                    </div>
                ) : (
                    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
                        <h1>Пожалуйста авторизуйтесь</h1>
                        <p>Если у вас нет учетной записи, пожалуйста зарегистрироваться.</p>
                    </div>
                )}
        </div>
    );
}
