"use client";

import { useState } from "react";
import { login } from "../../lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await login(email, password);
    if (res.access_token) {
      setMessage("Успешный вход!");
    } else {
      setMessage("Ошибка входа");
    }
  }

  return (
    <div>
      <h2>Вход</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email"
          value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Пароль"
          value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Войти</button>
      </form>
      <p>{message}</p>
    </div>
  );
}
