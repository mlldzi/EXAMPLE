# Docker и Развертывание

Вся система разработана для запуска в Docker-контейнерах, что обеспечивает консистентность окружения и упрощает развертывание. Файл `docker-compose.yml` в корне проекта является центральной точкой для управления всеми сервисами.

## 1. `docker-compose.yml`

Этот файл определяет все сервисы приложения, их конфигурацию сборки, зависимости, порты и переменные окружения.

**Основные секции и сервисы:**

*   **`version: '3.9'`**: Указывает версию синтаксиса Docker Compose.
*   **`services:`**: Определяет каждый контейнер как сервис.
    *   **`mongo:`**
        *   `image: mongo:latest` (или конкретная версия, например `mongo:6.0`)
        *   `ports: - "27017:27017"`: Пробрасывает порт MongoDB на хост-машину.
        *   `volumes: - mongo_data:/data/db`: Сохраняет данные MongoDB в именованном томе `mongo_data`, чтобы они не терялись при перезапуске контейнера.
        *   `restart: unless-stopped`: Автоматически перезапускать контейнер, если он не был остановлен вручную.
    *   **`redis:`**
        *   `image: redis:latest` (или конкретная версия, например `redis:7.0`)
        *   `ports: - "6379:6379"`: Пробрасывает порт Redis.
        *   `volumes: - redis_data:/data`:
        *   `restart: unless-stopped`
    *   **`user_service:`** (и аналогично `auth_service`)
        *   `build: ./backend/user_service`: Указывает путь к директории с `Dockerfile` для сборки образа.
        *   `depends_on: [mongo, redis]`: Сервис запустится только после старта MongoDB и Redis.
        *   `environment:`: Переменные окружения, передаваемые в контейнер.
            *   `MONGO_URI=mongodb://mongo:27017/user_db` (имя хоста `mongo` соответствует имени сервиса MongoDB в Docker Compose, `user_db` - имя базы данных).
            *   `REDIS_URL=redis://redis:6379/0`
            *   `JWT_SECRET_KEY=${JWT_SECRET_KEY}`: Загружает значение из файла `.env` в корне проекта.
            *   ... другие настройки из `backend/shared/config/settings.py`.
        *   `ports: - "8001:8000"`: Пробрасывает порт 8000 контейнера на порт 8001 хоста (для `user_service`, `auth_service` может быть на `8002:8000`).
        *   `volumes: - ./backend/user_service:/app - ./backend/shared:/app/backend/shared`: (Для разработки) Монтирует исходный код в контейнер, позволяя видеть изменения без пересборки образа. Для продакшена обычно исходный код копируется в образ на этапе сборки (`COPY . .` в Dockerfile).
        *   `restart: unless-stopped`
    *   **`celery_worker:`**
        *   `build: ./celery_worker`
        *   `depends_on: [redis]` (и `mongo`, если worker работает с БД)
        *   `environment:`
            *   `REDIS_URL=redis://redis:6379/0`
            *   `MONGO_URI=mongodb://mongo:27017/celery_db` (если нужно)
            *   `JWT_SECRET_KEY=${JWT_SECRET_KEY}` (если worker использует security утилиты)
        *   `volumes: - ./celery_worker:/app - ./backend/shared:/app/backend/shared`: (Для разработки).
        *   `restart: unless-stopped`
    *   **`frontend:`**
        *   `build: ./frontend`
        *   `ports: - "5173:5173"`: Пробрасывает порт Vite dev server или порт Nginx, если фронтенд собран для продакшена и раздается Nginx внутри контейнера.
        *   `volumes: - ./frontend:/app - /app/node_modules`: (Для разработки) Монтирует код фронтенда, но исключает `node_modules` из монтирования, чтобы использовались те, что установлены внутри контейнера (если `npm install` происходит в Dockerfile).
        *   `depends_on: [user_service, auth_service]`: (Опционально) Чтобы фронтенд стартовал, когда бэкенды уже доступны, хотя обычно фронтенд может стартовать и ожидать доступности API.
        *   `restart: unless-stopped`
    *   **(Опционально) `flower:`** (для мониторинга Celery)
        *   `image: mher/flower`
        *   `ports: ["5555:5555"]`
        *   `environment: [CELERY_BROKER_URL=redis://redis:6379/0, CELERY_RESULT_BACKEND=redis://redis:6379/0]`
        *   `depends_on: [redis, celery_worker]`
        *   `restart: unless-stopped`
*   **`volumes:`**: Определяет именованные тома для персистентного хранения данных.
    *   `mongo_data:`
    *   `redis_data:`

## 2. Dockerfiles

Каждый сервис (`user_service`, `auth_service`, `celery_worker`, `frontend`) имеет свой `Dockerfile`.

*   **Бэкенд сервисы и Celery Worker (`FROM python:3.x-slim`):**
    1.  Установка рабочей директории (`WORKDIR /app`).
    2.  Копирование `requirements.txt` и установка зависимостей (`RUN pip install --no-cache-dir -r requirements.txt`). Это кэшируется Docker'ом и не будет выполняться каждый раз, если `requirements.txt` не изменился.
    3.  Копирование всего остального кода проекта (`COPY . .`).
    4.  Копирование директории `backend/shared` (например, `COPY ../backend/shared /app/backend/shared`), чтобы общий код был доступен.
    5.  Указание команды для запуска (`CMD [...]`). Например, `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` для FastAPI или `CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]` для Celery.

*   **Фронтенд (`FROM node:18-alpine` или аналогичный):**
    1.  Установка рабочей директории (`WORKDIR /app`).
    2.  Копирование `package.json` и `package-lock.json` (или `yarn.lock`).
    3.  Установка зависимостей (`RUN npm install` или `RUN yarn install`).
    4.  Копирование остального кода (`COPY . .`).
    5.  **Для разработки**: `CMD ["npm", "run", "dev"]` (запускает Vite dev server).
    6.  **Для продакшена (Multi-stage build):**
        *   Первый этап (build stage): Сборка статических файлов (`RUN npm run build`).
        *   Второй этап (production stage, `FROM nginx:alpine` или другой легковесный сервер): Копирование собранных статических файлов из первого этапа (`COPY --from=build-stage /app/dist /usr/share/nginx/html`) и настройка Nginx для их раздачи.

## 3. Переменные Окружения и `.env` файл

*   Создайте файл `.env` в корне проекта (рядом с `docker-compose.yml`). Скопируйте содержимое из `.env.example` (если есть) и измените значения.
*   **Никогда не добавляйте `.env` файл в систему контроля версий!** `.gitignore` должен содержать строку `.env`.
*   Ключевые переменные:
    *   `JWT_SECRET_KEY`: **Обязательно сгенерируйте свой уникальный, сложный ключ!**
    *   `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`: Для инициализации MongoDB с пользователем (если требуется).
    *   Другие настройки для сервисов.
*   В `docker-compose.yml` переменные из `.env` файла доступны по синтаксису `${VARIABLE_NAME}`.

## 4. Основные Команды Docker Compose

*   **Сборка образов:**
    ```bash
    docker-compose build
    ```
    (Можно указать конкретный сервис: `docker-compose build user_service`)
*   **Запуск всех сервисов в фоновом режиме (-d, detached):**
    ```bash
    docker-compose up -d
    ```
*   **Запуск с пересборкой (если были изменения в Dockerfile или коде, который копируется):**
    ```bash
    docker-compose up -d --build
    ```
*   **Просмотр логов всех сервисов (в реальном времени с -f):**
    ```bash
    docker-compose logs -f
    ```
    (Логи конкретного сервиса: `docker-compose logs -f user_service`)
*   **Остановка и удаление контейнеров:**
    ```bash
    docker-compose down
    ```
*   **Остановка, удаление контейнеров и томов (данные будут удалены!):**
    ```bash
    docker-compose down -v
    ```
*   **Просмотр запущенных контейнеров, управляемых Compose:**
    ```bash
    docker-compose ps
    ```
*   **Выполнение команды внутри запущенного контейнера:**
    ```bash
    docker-compose exec user_service bash # Откроет bash-сессию в контейнере user_service
    ```

## 5. Рекомендации по Развертыванию (Production)

*   **Dockerfile для Продакшена**: Используйте multi-stage builds для фронтенда, чтобы итоговый образ содержал только статические файлы и легковесный веб-сервер (Nginx). Для бэкенда убедитесь, что не копируются ненужные файлы (например, `.git`, файлы тестов) и что используются не-root пользователи внутри контейнера.
*   **Переменные Окружения**: Не храните секреты в Docker-образах. Используйте `.env` файлы, которые передаются на сервер безопасным образом, или системы управления секретами (HashiCorp Vault, AWS Secrets Manager и т.д.).
*   **Базы Данных**: Для продакшена часто используются управляемые облачные сервисы баз данных (MongoDB Atlas, AWS RDS/DocumentDB, Redis Cloud) вместо запуска их в Docker-контейнерах на том же хосте, что и приложение. Это обеспечивает лучшую надежность, масштабируемость и возможности резервного копирования.
*   **Сеть и Безопасность**: Настройте фаервол, используйте HTTPS (например, с помощью Let's Encrypt и обратного прокси, такого как Nginx или Traefik перед вашими сервисами).
*   **Логирование**: Настройте централизованное логирование (ELK stack, Grafana Loki, облачные сервисы логирования).
*   **Мониторинг**: Настройте мониторинг производительности приложений (APM), состояния хостов и контейнеров (Prometheus, Grafana).
*   **CI/CD**: Автоматизируйте процессы сборки, тестирования и развертывания с помощью CI/CD пайплайнов (GitHub Actions, GitLab CI, Jenkins).
*   **Резервное копирование**: Регулярно создавайте резервные копии данных (базы данных, персистентные тома).

Эта заготовка предоставляет хорошую отправную точку для локальной разработки. Для перевода ее в полноценное продакшен-окружение потребуется дополнительная работа по обеспечению безопасности, надежности и масштабируемости. 