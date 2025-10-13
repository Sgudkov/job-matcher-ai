import Navbar from "../components/Navbar";
import { AuthProvider, useAuth } from "./context/AuthContext";
import "../styles/globals.css";

export const metadata = {
  title: 'Мое приложение',
  description: 'Описание приложения',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>
        <AuthProvider>
          <Navbar />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
