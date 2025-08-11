import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  darkMode: 'class', // enable class-based dark mode
  theme: {
    extend: {
      colors: {
        darkBg: '#0D0D0D', // black
        darkAccent: '#D32F2F', // red accent
      },
    },
  },
  plugins: [react(), tailwindcss()],
})
