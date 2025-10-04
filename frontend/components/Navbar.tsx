import Link from "next/link";

export default function Navbar() {
  return (
    <nav>
      <Link href="/auth/login">Вход</Link> |
      <Link href="/auth/register">Регистрация</Link> |
      <Link href="/auth/profile">Профиль</Link>
    </nav>
  );
}
