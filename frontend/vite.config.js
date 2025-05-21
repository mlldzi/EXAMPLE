import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Порт для фронтенда
    proxy: {
      // Прокси для запросов к API, чтобы избежать CORS проблем при разработке
      '/api': {
        target: 'http://127.0.0.1:8000', // URL твоего FastAPI бэкенда
        changeOrigin: true,
      }
    }
  }
}) 