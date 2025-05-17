from celery import Celery
import os

# Используем переменную окружения REDIS_URL, которая должна быть установлена
# в docker-compose.yml для сервисов, использующих этот клиент.
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Этот экземпляр Celery используется только для ОТПРАВКИ задач,
# а не для выполнения. Фактическое имя приложения ('tasks_client') здесь
# не так критично, как broker и backend URL.
# Имена задач (например, 'add_numbers', 'send_email_task') должны совпадать
# с теми, что зарегистрированы в celery_worker/tasks.py (либо через @app.task(name=...)
# либо как <module_name>.<function_name>).
celery_app = Celery('tasks_client', broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=os.getenv('TZ', 'UTC'), # Можно также настроить через переменную окружения
    enable_utc=True,
    task_track_started=True,
    result_expires=int(os.getenv('CELERY_RESULT_EXPIRES', 3600)) # Время хранения результатов
)

def call_add_numbers(x: int, y: int):
    """
    Отправляет задачу 'add_numbers' в очередь Celery.
    Имя задачи 'add_numbers' должно соответствовать зарегистрированному в worker'е.
    """
    return celery_app.send_task('add_numbers', args=[x, y])

def call_send_email(email_to: str, subject: str, body: str):
    """
    Отправляет задачу 'send_email_task' в очередь Celery.
    Имя задачи 'send_email_task' должно соответствовать зарегистрированному в worker'е.
    """
    return celery_app.send_task('send_email_task', args=[email_to, subject, body])

# Можно добавить больше функций-оберток для других задач по мере их появления. 