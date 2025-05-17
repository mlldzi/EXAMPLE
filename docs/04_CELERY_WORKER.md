# Celery Worker

Celery worker используется в проекте для выполнения фоновых (асинхронных) задач. Это позволяет разгрузить основные веб-сервисы от длительных операций, улучшая отклик API и общее взаимодействие с пользователем.

## 1. Назначение

*   **Выполнение длительных операций**: Задачи, которые могут занять значительное время (например, обработка больших файлов, отправка email-рассылок, сложные вычисления), должны выполняться в фоне, чтобы не блокировать основной поток обработки HTTP-запросов.
*   **Периодические задачи**: Celery также поддерживает запуск задач по расписанию (Celery Beat), что полезно для регулярных операций (например, генерация отчетов, очистка старых данных). (Celery Beat не сконфигурирован в базовой заготовке, но может быть легко добавлен).
*   **Надежность**: Celery обеспечивает механизмы повторных попыток и обработки ошибок для задач.

## 2. Конфигурация

*   **Директория**: `celery_worker/`
*   **Основные файлы**:
    *   `tasks.py`: Здесь определяется экземпляр приложения Celery и регистрируются сами задачи.
    *   `requirements.txt`: Содержит зависимости, необходимые для worker'а (в основном `celery` и `redis`).
    *   `Dockerfile`: Конфигурация для сборки Docker-образа worker'а.

### `tasks.py` (Пример)

```python
from celery import Celery
import time
import os

# Получаем URL Redis из переменной окружения
# REDIS_URL должен быть в формате redis://<host>:<port>/<db_number>
# Например, redis://redis:6379/0, где 'redis' - имя сервиса из docker-compose.yml
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Инициализация приложения Celery
# 'tasks' - это имя текущего модуля, оно будет префиксом для имен задач
# broker - URL брокера сообщений (Redis)
# backend - URL для хранения результатов задач (можно использовать тот же Redis)
app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# Опциональные настройки Celery (можно вынести в отдельный config файл)
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Допустимые форматы контента
    result_serializer='json',
    timezone='Europe/Moscow', # Пример таймзоны
    enable_utc=True,
    # Пример настройки для отслеживания состояния задачи и ее результата
    task_track_started=True, 
    # Время хранения результатов задач (в секундах)
    result_expires=3600, # 1 час
)

# Пример определения задачи
@app.task(bind=True, name='add_numbers') # 'name' - опциональное явное имя задачи
def add_numbers(self, x: int, y: int) -> int:
    """Простая задача для сложения двух чисел."""
    # self.request.id - уникальный ID задачи
    print(f"Task {self.request.id}: Adding {x} + {y}")
    time.sleep(5) # Имитация длительной операции
    result = x + y
    print(f"Task {self.request.id}: Result is {result}")
    return result

@app.task(name='send_email_task')
def send_email_task(email_to: str, subject: str, body: str):
    """
    Пример задачи для отправки email.
    Реальная логика отправки email здесь не показана.
    """
    print(f"Sending email to {email_to} with subject '{subject}'...")
    # Здесь могла бы быть интеграция с SMTP-сервисом
    time.sleep(10) # Имитация отправки
    print(f"Email to {email_to} sent.")
    return {"status": "success", "email": email_to}

# Чтобы запустить worker из директории celery_worker:
# celery -A tasks worker -l info

# Чтобы посмотреть зарегистрированные задачи:
# celery -A tasks inspect registered
```

### `Dockerfile`

Dockerfile для `celery_worker` настраивает Python окружение, устанавливает зависимости и указывает команду для запуска Celery worker'а:
`CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]`

### `docker-compose.yml`

Сервис `celery_worker` в `docker-compose.yml` зависит от `redis` и использует переменную окружения `REDIS_URL` для подключения к брокеру.

```yaml
# ...
  redis:
    image: redis
    ports:
      - "27017:27017" # Ошибка: Redis обычно на 6379, MongoDB на 27017. Исправлено ниже.
      - "6379:6379"
  # ...
  celery_worker:
    build: ./celery_worker
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0 # Передается в tasks.py
      # Также сюда можно передавать MONGO_URI, если задачи работают с БД
      # - MONGO_URI=mongodb://mongo:27017 
    volumes: # Опционально, для удобства разработки, чтобы не пересобирать образ при каждом изменении кода
      - ./celery_worker:/app 
      - ./backend/shared:/app/backend/shared # Если worker использует общие модули
# ...
```
Важно: Если `celery_worker` использует код из `backend/shared/`, необходимо убедиться, что `Dockerfile` для `celery_worker` копирует эту директорию, и `PYTHONPATH` настроен соответствующим образом, либо импорты в `tasks.py` используют корректные пути (например, если `backend/shared` копируется в `/app/shared`, то импорты могут быть `from shared.models import ...`). В текущей настройке `backend/shared` копируется в `/app/backend/shared`, поэтому импорты вроде `from backend.shared.config import settings` должны работать.

## 3. Вызов Задач

Задачи Celery могут быть вызваны из любого бэкенд-сервиса (например, `auth_service` или `user_service`), у которого есть доступ к экземпляру приложения Celery и настроенному брокеру.

**Пример вызова задачи из FastAPI эндпоинта:**

Предположим, у нас есть экземпляр Celery `app` из `celery_worker.tasks` доступный в нашем FastAPI сервисе.
Это можно сделать, создав отдельный клиентский модуль для Celery в `backend/shared/utils/celery_client.py` или напрямую импортируя `app` из `celery_worker.tasks` (потребуется правильная настройка `PYTHONPATH` или установка `celery_worker` как пакета).

**`backend/shared/utils/celery_client.py` (рекомендуемый подход):**
```python
from celery import Celery
import os

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Этот экземпляр используется только для ОТПРАВКИ задач, а не для выполнения.
# Имена задач ('tasks.add_numbers') должны совпадать с теми, что зарегистрированы в worker'е.
celery_app = Celery('tasks_client', broker=REDIS_URL, backend=REDIS_URL) # Имя может быть любым, но broker/backend важны

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    task_track_started=True, # Позволяет отслеживать статус
    result_expires=3600,
)

# Функции-обертки для вызова задач
def call_add_numbers(x: int, y: int):
    # tasks.add_numbers - это <module_name>.<task_name> из celery_worker/tasks.py
    # или явное имя, указанное в @app.task(name='add_numbers')
    return celery_app.send_task('add_numbers', args=[x, y])

def call_send_email(email_to: str, subject: str, body: str):
    return celery_app.send_task('send_email_task', args=[email_to, subject, body])

```

**В FastAPI эндпоинте (`user_service/app.py` или `auth_service/app.py`):**
```python
from fastapi import FastAPI, BackgroundTasks
from backend.shared.utils.celery_client import call_add_numbers, call_send_email # Пример импорта
# ... другие импорты

app = FastAPI()

@app.post("/api/v1/users/register")
async def register_user(user_data: dict): # Замените dict на Pydantic модель
    # ... логика создания пользователя ...
    
    # Отправка приветственного email как фоновая задача
    # .delay() - это шорткат для .send_task().args(...)
    # celery_app.send_task('send_email_task', args=[user_data['email'], "Welcome!", "Thanks for registering!"])
    task_result = call_send_email(user_data['email'], "Welcome!", "Thanks for registering!")
    
    # task_result.id содержит ID задачи, который можно сохранить для отслеживания статуса
    return {"message": "User registered, welcome email is being sent.", "task_id": task_result.id}

@app.get("/api/v1/calculate")
async def calculate_sum(x: int, y: int):
    task_result = call_add_numbers(x,y)
    return {"message": "Calculation task sent.", "task_id": task_result.id}

@app.get("/api/v1/task_status/{task_id}")
async def get_task_status(task_id: str):
    # celery_app - экземпляр Celery из celery_client.py
    from backend.shared.utils.celery_client import celery_app 
    
    async_result = celery_app.AsyncResult(task_id)
    
    if async_result.ready(): # Задача выполнена (успешно или с ошибкой)
        if async_result.successful():
            return {"task_id": task_id, "status": async_result.status, "result": async_result.result}
        else: # Задача завершилась с ошибкой
            return {"task_id": task_id, "status": async_result.status, "error": str(async_result.info)} # .info содержит исключение
    else: # Задача еще выполняется или в очереди
        return {"task_id": task_id, "status": async_result.status}

```
Примечание: Для использования `celery_app.AsyncResult(task_id)` для получения статуса и результата, `backend` в конфигурации Celery (`celery_app` и `app` в `tasks.py`) должен быть настроен (например, на Redis).

## 4. Взаимодействие с Redis

*   **Брокер Сообщений**: Celery использует Redis для передачи сообщений о задачах от веб-сервиса к worker'ам. Когда задача вызывается (`.delay()` или `.send_task()`), она помещается в очередь в Redis. Worker'ы слушают эти очереди и забирают задачи на выполнение.
*   **Хранилище Результатов (Backend)**: Redis также может использоваться для хранения результатов выполнения задач. Это позволяет веб-сервису запрашивать статус и результат задачи по ее ID.

## 5. Масштабирование

Можно запустить несколько экземпляров `celery_worker` сервиса для параллельной обработки задач. Docker Compose позволяет легко масштабировать количество worker'ов:
```bash
docker-compose up -d --scale celery_worker=3
```
Это запустит 3 контейнера `celery_worker`, каждый из которых будет обрабатывать задачи из очереди.

## 6. Мониторинг

Для мониторинга задач Celery можно использовать инструмент Flower. Это веб-интерфейс, который показывает информацию о worker'ах, задачах, очередях и т.д. Его можно добавить как еще один сервис в `docker-compose.yml`.

Пример добавления Flower:
```yaml
# в docker-compose.yml
  flower:
    image: mher/flower
    ports:
      - "5555:5555" # Веб-интерфейс Flower
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      # Если используется backend для результатов:
      - CELERY_RESULT_BACKEND=redis://redis:6379/0 
    depends_on:
      - redis
      - celery_worker # Чтобы Flower стартовал после worker'а (не обязательно, но логично)
```

После этого Flower будет доступен по адресу `http://localhost:5555`.

---

Celery worker является важной частью архитектуры для создания отзывчивых и масштабируемых приложений. 