# Обзор Проекта-Заготовки для Хакатона

## 1. Назначение

Этот проект представляет собой универсальную и масштабируемую заготовку, предназначенную для быстрого старта разработки на хакатонах. Он включает в себя набор современных технологий и настроенную базовую структуру, позволяя команде сосредоточиться на реализации бизнес-логики, а не на первоначальной настройке окружения.

## 2. Технологический Стек

**Бэкенд:**
*   **FastAPI**: Современный, быстрый (высокопроизводительный) веб-фреймворк для создания API на Python 3.13+.
*   **Python**: Основной язык программирования для бэкенда.
*   **Celery**: Система для выполнения распределенных асинхронных задач.
*   **Motor**: Асинхронный драйвер Python для MongoDB.
*   **Pydantic**: Валидация данных и управление настройками.
*   **python-jose & passlib**: Для JWT-аутентификации и хеширования паролей.

**Фронтенд:**
*   **Vue.js 3**: Прогрессивный JavaScript-фреймворк для создания пользовательских интерфейсов.
*   **Vite**: Современный инструмент для сборки фронтенда, обеспечивающий чрезвычайно быструю разработку.
*   **TypeScript**: Статически типизированный JavaScript, улучшающий читаемость и поддержку кода.
*   **Pinia**: Система управления состоянием для Vue.js.
*   **Vue Router**: Официальный роутер для Vue.js.
*   **Tailwind CSS**: Утилитарный CSS-фреймворк для быстрой стилизации.
*   **Axios**: HTTP-клиент для взаимодействия с API.

**Базы данных и Брокеры:**
*   **MongoDB**: NoSQL документо-ориентированная база данных.
*   **Redis**: Хранилище структур данных в памяти, используемое как кэш и брокер сообщений для Celery.

**Контейнеризация и Оркестрация:**
*   **Docker**: Платформа для разработки, доставки и запуска приложений в контейнерах.
*   **Docker Compose**: Инструмент для определения и запуска многоконтейнерных Docker-приложений.

## 3. Как Быстро Начать

1.  **Клонировать репозиторий:**
    ```bash
    git clone <URL_РЕПОЗИТОРИЯ>
    cd <НАЗВАНИЕ_ПРОЕКТА>
    ```
2.  **Настроить переменные окружения:**
    Скопируйте `.env.example` (если есть) в `.env` и измените значения при необходимости. Ключевые переменные:
    *   `JWT_SECRET_KEY`: **Обязательно измените на свой уникальный ключ!**
    *   `MONGO_URI`
    *   `REDIS_URL`
    (Подробнее см. `backend/shared/config/settings.py`)

3.  **Собрать и запустить сервисы:**
    ```bash
    docker-compose build
    docker-compose up -d
    ```
4.  **Проверка работоспособности:**
    *   Бэкенд сервисы будут доступны на портах, указанных в `docker-compose.yml` (например, `user_service` на `http://localhost:8001`, `auth_service` на `http://localhost:8002`). Каждый сервис имеет эндпоинт `/docs` для OpenAPI (Swagger) документации.
    *   Фронтенд будет доступен на `http://localhost:5173`.
    *   Celery worker будет обрабатывать задачи (пока нет интерфейса для их постановки, но можно проверить логи).

5.  **Остановка сервисов:**
    ```bash
    docker-compose down
    ```