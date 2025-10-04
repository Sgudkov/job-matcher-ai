'use client';

import { useAuth } from "../app/context/AuthContext";


export default function HomePage() {
    const { user } = useAuth();
    console.log("HomePage", user);
    return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
            {user ?
                (
                    <div>
                        <h1>Добро пожаловать на страницу <span>{user.first_name}</span> <span>{user.last_name}</span> </h1>
                    </div>

                ) : (
                    <h1>Пожалуйста авторизуйтесь</h1>
                )}
        </div>
    );
}
