from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "fastapi_monolith_db"
    JWT_SECRET_KEY: str = "your-secret-key-please-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()

@lru_cache
def get_settings() -> Settings:
    return settings 