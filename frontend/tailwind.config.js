/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#7C241D',
        secondary: '#9A6A2F',
        cta: '#0F766E',
        background: '#F5EFE4',
        text: '#211A16',
        ink: '#211A16',
        paper: '#FFFDF8',
        parchment: '#E9DDC7',
        muted: '#6F6259',
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans', 'system-ui', 'sans-serif'],
        serif: ['"Noto Serif"', 'Georgia', 'serif'],
      },
      boxShadow: {
        'clay': '0 18px 50px rgba(46, 35, 26, 0.10), 0 1px 0 rgba(255,255,255,0.9) inset',
        'clay-active': '0 8px 22px rgba(46, 35, 26, 0.12), 0 1px 0 rgba(255,255,255,0.8) inset',
        'paper': '0 18px 55px rgba(45, 34, 24, 0.12)',
        'soft': '0 10px 28px rgba(45, 34, 24, 0.08)',
      },
    },
  },
  plugins: [],
}
