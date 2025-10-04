"use client";

import { useEffect, useState } from "react";
import { me, logout } from "../../lib/api";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    me().then(setUser);
  }, []);

  if (!user) return <p>Загрузка...</p>;

  return (
    <div>
      <h2>Профиль</h2>
      <p>Email: {user.email}</p>
      <p>ID: {user.id}</p>
      <button onClick={logout}>Выйти</button>
    </div>
  );
}
