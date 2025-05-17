from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from backend.shared.models.auth_schemas import Token, UserCreate, UserRead, RefreshTokenRequest
from backend.shared.models.user_schemas import UserInDB
from backend.shared.utils.security import create_access_token, create_refresh_token, verify_password, get_password_hash, decode_jwt_token, JWTAuthenticationError
from backend.shared.config import settings
# Для работы с БД (примерный импорт, нужно будет создать/адаптировать db_utils или crud операции)
# from backend.shared.db.mongodb_utils import get_database # Пример
# from backend.auth_service.crud import user_crud # Пример

# Заглушка для базы данных и CRUD операций
# В реальном приложении здесь будет взаимодействие с MongoDB
# Для примера, будем использовать простой словарь как БД
fake_users_db = {} 

# Заглушка для функции получения текущего пользователя по токену
# В реальном приложении эта функция будет частью зависимостей FastAPI
async def get_current_active_user(token: str = Depends(settings.OAUTH2_SCHEME)) -> UserInDB:
    try:
        payload = decode_jwt_token(token)
        if payload.token_type != "ACCESS":
            raise JWTAuthenticationError("Invalid token type for authentication")
        
        user_id = payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Здесь должен быть поиск пользователя в БД по user_id
        user_data = fake_users_db.get(user_id) # Заглушка
        if user_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Убедимся, что user_data содержит все необходимые поля UserInDB
        # В реальном приложении это будет объект, полученный из БД
        return UserInDB(**user_data, id=user_id) # Возвращаем UserInDB
    except JWTAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e: # Общий обработчик на случай других ошибок
        print(f"Error in get_current_active_user: {e}") # Логирование ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user retrieval",
            headers={"WWW-Authenticate": "Bearer"},
        )


router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_new_user(user_in: UserCreate):
    # Проверка, существует ли пользователь с таким email
    for user_id, user_data in fake_users_db.items():
        if user_data.get("email") == user_in.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    hashed_password = get_password_hash(user_in.password)
    # В реальном приложении ID будет генерироваться базой данных
    # Мы используем email как временный ID для простоты заглушки
    user_id = user_in.email 
    
    # Сохраняем пользователя (включая все поля UserInDB)
    user_in_db_data = user_in.model_dump()
    user_in_db_data.update({"hashed_password": hashed_password, "is_active": True, "is_superuser": False, "role": "user"})
    
    # Убедимся, что все необходимые поля для UserInDB есть
    # Это очень упрощенная версия
    user_entry = {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_superuser": False,
        "role": "user",
        # created_at и updated_at должны добавляться автоматически или через BaseDBModel
    }
    fake_users_db[user_id] = user_entry
    
    return UserRead(**user_entry) # Возвращаем данные пользователя без пароля


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Поиск пользователя по email (username из OAuth2PasswordRequestForm)
    user_id = form_data.username # Используем email как username
    user_data_in_db = fake_users_db.get(user_id)

    if not user_data_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserInDB(**user_data_in_db) # Создаем объект UserInDB из данных в "БД"
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = create_access_token(subject=str(user.id)) # subject должен быть строкой
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_request: RefreshTokenRequest):
    try:
        payload = decode_jwt_token(refresh_request.refresh_token)
        if payload.token_type != "REFRESH":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token type for refresh"
            )
        
        user_id = payload.sub
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials for refresh token",
            )
        
        # Проверка, что пользователь все еще существует и активен (опционально, но рекомендуется)
        user_data = fake_users_db.get(user_id) # Заглушка
        if not user_data or not user_data.get("is_active"):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found or inactive"
            )

        new_access_token = create_access_token(subject=user_id)
        # Опционально: можно также генерировать новый refresh_token (refresh token rotation)
        # new_refresh_token = create_refresh_token(subject=user_id)
        # и инвалидировать старый refresh_token
        
        return Token(access_token=new_access_token, refresh_token=refresh_request.refresh_token, token_type="bearer")

    except JWTAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    # current_user уже является экземпляром UserInDB благодаря get_current_active_user
    # Просто преобразуем его в UserRead для ответа
    return UserRead.model_validate(current_user) 