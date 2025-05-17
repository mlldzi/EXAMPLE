FROM python:3.13.3-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../backend/shared /app/shared
COPY . .
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"] 