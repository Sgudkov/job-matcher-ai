"use client";
import { useAuth } from '../context/AuthContext';
import CreateResume from "./CreateResume";
import CreateVacancy from "./CreateVacancy";

export default function Create() {
  const { user } = useAuth();

  return (
    <div className="max-w-3xl mx-auto p-6">
      {user?.role === 'candidate' ? (
        <CreateResume />
      ) : (
        <CreateVacancy />
      )}
    </div>
  );
}
