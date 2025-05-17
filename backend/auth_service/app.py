from fastapi import FastAPI
from backend.shared.config import settings
from backend.auth_service.api.v1.endpoints import auth as auth_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME + " - Auth Service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0" # Пример версии
)

# Подключаем роутер для эндпоинтов аутентификации
app.include_router(auth_v1_router.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} - Auth Service"}

# Пример health check эндпоинта
@app.get("/health", tags=["Health"])
async def health_check():
    # В реальном приложении здесь можно проверять доступность БД, Redis и т.д.
    return {"status": "ok"}

# Добавить обработчики исключений, если нужны кастомные
# from backend.shared.exceptions.custom import NotFoundException, BadRequestException
# from fastapi.responses import JSONResponse
#
# @app.exception_handler(NotFoundException)
# async def not_found_exception_handler(request: Request, exc: NotFoundException):
#     return JSONResponse(
#         status_code=404,
#         content={"detail": exc.detail},
#     )
#
# @app.exception_handler(BadRequestException)
# async def bad_request_exception_handler(request: Request, exc: BadRequestException):
#     return JSONResponse(
#         status_code=400,
#         content={"detail": exc.detail},
#     )


# Если вы хотите инициализировать какие-то ресурсы при старте приложения (например, подключение к БД)
# @app.on_event("startup")
# async def startup_event():
#     # app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
#     # app.db = app.mongodb_client[settings.MONGO_DB_AUTH] # или другое имя БД для сервиса
#     print("Auth service started...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     # app.mongodb_client.close()
#     print("Auth service shutting down...") 