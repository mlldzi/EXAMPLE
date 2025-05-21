# Lightweight FastAPI Project Template

Это легковесная заготовка проекта на FastAPI с асинхронным драйвером Motor для MongoDB и аутентификацией JWT.

## Быстрый старт

1.  **Настройте переменные окружения:**
    Скопируйте `.env.example` в `.env` и заполните значения:
    ```bash
    cp .env.example .env
    # Отредактируйте .env файл
    ```
    Ключевые переменные:
    *   `MONGO_URI`: Строка подключения к MongoDB.
    *   `MONGO_DB_NAME`: Имя базы данных.
    *   `JWT_SECRET_KEY`: Секретный ключ для JWT (ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ!).
    *   `PROJECT_NAME` (опционально): Название вашего проекта.
    *   `ACCESS_TOKEN_EXPIRE_MINUTES` (опционально): Время жизни access токена.

2.  **Сборка и запуск сервисов:**
    ```bash
    docker-compose up --build -d
    ```

3.  **Доступные эндпоинты:**
    *   Бэкенд: `http://localhost:8000`
    *   Документация API (Swagger): `http://localhost:8000/docs`
    *   Документация API (ReDoc): `http://localhost:8000/redoc`

4.  **Остановка сервисов:**
    ```bash
    docker-compose down
    ```

## Структура

Структура проекта ориентирована на атомарность и расширяемость. Основные компоненты находятся в директории `backend/app/`.
