import type { Config } from 'tailwindcss'

// Tailwind CSS v4 использует новый синтаксис @import "tailwindcss"
// Кастомные цвета определены в globals.css через CSS-переменные
const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
}
export default config
