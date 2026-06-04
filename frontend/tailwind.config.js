/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5',
        secondary: '#818CF8',
        cta: '#22C55E',
        background: '#EEF2FF',
        text: '#312E81',
      },
      fontFamily: {
        sans: ['"Baloo 2"', 'sans-serif'],
      },
      boxShadow: {
        'clay': 'inset -4px -4px 8px rgba(0,0,0,0.1), inset 4px 4px 8px rgba(255,255,255,0.7), 4px 4px 10px rgba(0,0,0,0.05)',
        'clay-active': 'inset -2px -2px 4px rgba(0,0,0,0.1), inset 2px 2px 4px rgba(255,255,255,0.7), 2px 2px 5px rgba(0,0,0,0.05)',
      },
    },
  },
  plugins: [],
}
