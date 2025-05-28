from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.session import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints import users, auth, term_document_relations, terms, documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий запуска и остановки приложения."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Настройка CORS (разрешаем все источники, методы и заголовки для простоты хакатона)
# В продакшене следует ограничить allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Или укажите конкретные источники, например ["http://localhost", "http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(terms.router, prefix="/api/v1/terms", tags=["terms"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(term_document_relations.router, prefix="/api/v1/term_document_relations", tags=["term_document_relations"])

# TODO: Добавить другие настройки middleware при необходимости. 