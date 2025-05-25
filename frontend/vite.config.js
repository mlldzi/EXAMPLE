import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const isDocker = process.env.DOCKER_RUN === 'true';
const API_URL = isDocker
  ? 'http://host.docker.internal:8000'
  : 'http://localhost:8000';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Порт для фронтенда
    proxy: {
      // Прокси для запросов к API, чтобы избежать CORS проблем при разработке
      '/api': {
        target: API_URL,
        changeOrigin: true,
      }
    },
    watch: {
      usePolling: true,
      interval: 1000,
    },
  }
}) 
// host.docker.internal — это специальное имя, которое внутри контейнера указывает на вашу хост-машину (Windows).
// в теории надо было бы использовать 127.0.0.1, но не работает