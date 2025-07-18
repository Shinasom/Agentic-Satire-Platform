/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['var(--font-lora)', 'serif'],
        sans: ['var(--font-inter)', 'sans-serif'],
      },
      colors: {
        brand: {
          red: '#D42D2F'
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}