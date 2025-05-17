from celery import Celery

app = Celery('tasks', broker='redis://redis:6379/0')

@app.task
def background_task(x, y):
    return x + y 