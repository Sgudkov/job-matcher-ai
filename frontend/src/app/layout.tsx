import Navbar from "../components/Navbar";
import { AuthProvider, useAuth } from "@/src/app/context/AuthContext";
import { Toaster } from 'react-hot-toast';
import "@/src/styles/globals.css";

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
            <Toaster position="top-right" />
        </AuthProvider>
      </body>
    </html>
  );
}
