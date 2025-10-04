"use client";

import { useState } from "react";
import { register } from "../../lib/api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await register(email, password);
    if (res.id) {
      setMessage("Регистрация успешна!");
    } else {
      setMessage("Ошибка регистрации");
    }
  }

  return (
    <div>
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email"
          value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Пароль"
          value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Зарегистрироваться</button>
      </form>
      <p>{message}</p>
    </div>
  );
}
