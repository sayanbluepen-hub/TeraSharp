/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        gis: {
          bg: '#0a0e1a',
          surface: '#111827',
          card: '#1a2235',
          border: '#1e3a5f',
          accent: '#0ea5e9',
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
          text: '#e2e8f0',
          muted: '#64748b',
        }
      }
    },
  },
  plugins: [],
}
