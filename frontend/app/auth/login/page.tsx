"use client";

import { useState } from "react";
import { fetchUser, login as loginApi } from "../../../lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import LoginForm from "./LoginForm";

export default function LoginPage() {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
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
      alert("Неправильное имя пользователя или пароль");
    }
  }

  return (
    <LoginForm
    username={name}
    setUsername={setName}
    password={password}
    setPassword={setPassword}
    onSubmit={handleSubmit} />

  );
}
