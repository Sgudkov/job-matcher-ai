// app/api/vacancies/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  // Замените на реальные данные из вашей БД
  const vacancies = [
    {
      id: '1',
      title: 'Frontend Developer (React)',
      company: 'TechCorp',
      location: 'Москва',
      salary: 150000,
      description: 'Мы ищем опытного Frontend разработчика для работы над современными веб-приложениями...',
      employmentType: 'Полная занятость',
      experience: '1-3 года',
      skills: ['React', 'TypeScript', 'Next.js', 'CSS'],
      createdAt: '2024-01-15',
    },
    {
      id: '2',
      title: 'Backend Developer (Python)',
      company: 'DataSystems',
      location: 'Удаленно',
      salary: 180000,
      description: 'Разработка высоконагруженных backend систем и API...',
      employmentType: 'Удаленная работа',
      experience: '3-6 лет',
      skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
      createdAt: '2024-01-14',
    },
    // Добавьте больше вакансий...
  ];

  return NextResponse.json(vacancies);
}
