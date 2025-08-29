import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  // Vite dev server settings
  server: {
    host: '0.0.0.0', // expose on LAN
    port: 5173
  },

  // Tailwind / project settings
  plugins: [react(), tailwindcss()],
  
  // Optional dark mode / theme settings
  css: {
    // If you want to use Tailwind dark mode
    preprocessorOptions: {
      // can add if needed
    }
  },
  // Tailwind / custom theme colors
  theme: {
    extend: {
      colors: {
        darkBg: '#0D0D0D',      // black
        darkAccent: '#D32F2F',  // red accent
      },
    },
  },

  // Enable class-based dark mode if using Tailwind
  darkMode: 'class',
})
