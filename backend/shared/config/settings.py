from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Настройки БД
    MONGO_URI: str = "mongodb://mongo:27017/mydatabase" # Добавил имя БД
    REDIS_URL: str = "redis://redis:6379/0"

    # Настройки JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-please-change-in-prod" # !!! ЗАМЕНИТЬ !!!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 минут
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 дней

    # Настройки CORS (если фронтенд на другом домене/порту)
    # BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Дополнительные настройки
    # FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = None
    # FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
        )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 