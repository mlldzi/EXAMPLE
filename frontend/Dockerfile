# Используем официальный образ Node.js
FROM node:24-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json и устанавливаем зависимости
COPY package*.json ./
RUN npm ci

# Копируем остальной код приложения
COPY . .

# Открываем порт Vite development server
EXPOSE 3000

# Команда для запуска development server
CMD ["npx", "vite", "--host"] 