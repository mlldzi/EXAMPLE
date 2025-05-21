from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer

from app.db.session import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import decode_token
from app.crud.user import CRUDUser
from app.models.user import UserPublic
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") # URL для получения токена

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Зависимость для получения асинхронной сессии базы данных."""
    # Используем yield для создания контекстного менеджера
    # Соединение управляется функциями connect_to_mongo/close_mongo_connection в lifespan
    try:
        db = await get_database()
        yield db
    except Exception as e:
        # В реальном приложении здесь может быть логирование ошибки
        print(f"Ошибка при получении сессии базы данных: {e}")
        # В зависимости от требований, можно пробросить исключение или вернуть None
        # Сейчас просто пробрасываем, FastAPI обработает ее как 500 Internal Server Error
        raise 

async def get_current_user(
    token: str = Security(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserPublic:
    """Зависимость для получения текущего аутентифицированного пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"": "Bearer"},
    )
    
    # Декодируем токен
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Получаем user_id из полезной нагрузки токена
    user_id_str = payload.get("sub")
    if user_id_str is None:
         raise credentials_exception

    try:
        user_id = UUID(user_id_str) # Преобразуем строку в UUID
    except ValueError:
         raise credentials_exception

    # Получаем пользователя из базы данных
    user_crud = CRUDUser(db)
    user = await user_crud.get_by_id(user_id=user_id)

    if user is None:
        raise credentials_exception # Пользователь не найден в БД

    # Конвертируем модель, сериализуя created_at в ISO формат
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    return UserPublic(**user_dict) 