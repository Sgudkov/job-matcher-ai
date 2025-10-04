"use client";

import { useState } from "react";
import { fetchUser, login as loginApi } from "../../../lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();
  const { login } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await loginApi(name, password);
    if (res.access_token) {
      const userData = await fetchUser(res.access_token);
      login(res.access_token, userData);
      router.push("/");
    } else {
      setMessage("Ошибка входа");
    }
  }

  return (
    <div>
      <h2>Вход</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username"
          value={name} onChange={(e) => setName(e.target.value)} />
        <input type="password" placeholder="Пароль"
          value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Войти</button>
      </form>
      <p>{message}</p>
    </div>
  );
}
