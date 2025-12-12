/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1F7368',
        secondary: '#63D7C7',
        tertiary: '#004F4D',
        'soft-accent': '#B3EDEB',
        'warm-accent': '#FFD187',
        'neutral-dark': '#181C19',
        'neutral-light': '#FFFAF3',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(31, 115, 104, 0.08)',
        'medium': '0 8px 30px rgba(31, 115, 104, 0.12)',
        'large': '0 12px 40px rgba(31, 115, 104, 0.16)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [],
}
