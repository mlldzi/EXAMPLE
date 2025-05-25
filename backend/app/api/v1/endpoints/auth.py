from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone

from app.core.config import settings # Импорт settings
from app.models.user import UserCreate, UserPublic, UserLoginRequest
from app.models.token import TokenResponse, RefreshTokenInDB, RefreshTokenRequest
from app.crud.user import CRUDUser
from app.db.session import get_database, REFRESH_TOKENS_COLLECTION
from app.core.security import create_access_token, verify_password
from pymongo.errors import DuplicateKeyError
from app.models.base import HTTPError

from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import uuid4

router = APIRouter()

async def _authenticate_user(email: str, password: str, db: AsyncIOMotorDatabase) -> UserPublic:
    """Аутентифицирует пользователя по email и паролю."""
    user_crud = CRUDUser(db)
    user = await user_crud.get_by_email(email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Предполагаем, что UserPublic совместим с моделью пользователя из CRUD
    # Если user из CRUD имеет другой тип, здесь нужна будет конвертация
    # или функция должна возвращать тот тип, который вернул user_crud.get_by_email
    # и который содержит user.id, user.roles и т.д.
    # На данный момент, предполагая, что user - это уже нужная модель (например, UserInDB)
    # и его поля доступны.
    return user # Возвращаем полную модель пользователя из БД

async def _create_token_response(user: UserPublic, db: AsyncIOMotorDatabase) -> TokenResponse:
    """Создает access и refresh токены для пользователя."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "roles": [role.value for role in user.roles]
            },
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_value = str(uuid4())
    refresh_token_db_obj = RefreshTokenInDB(
        user_id=user.id,
        refresh_token=refresh_token_value,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )
    await db[REFRESH_TOKENS_COLLECTION].insert_one(refresh_token_db_obj.model_dump(by_alias=True))
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token_value, 
        expires_in=access_token_expires.total_seconds()
    )

def _create_access_token_for_user(user: UserPublic) -> tuple[str, timedelta]:
    """Создает только access токен для пользователя и возвращает токен и время его жизни."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "roles": [role.value for role in user.roles],
            "refresh_id": str(uuid4()),  # Добавляем случайный идентификатор для уникальности нового access токена
        },
        expires_delta=access_token_expires
    )
    return access_token, access_token_expires

@router.post(
    "/register", 
    response_model=UserPublic, 
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": HTTPError,
            "description": "Ошибка при регистрации пользователя (например, email или имя пользователя уже существуют)"
        }
    }
)
async def register_user(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserPublic:
    """Регистрация нового пользователя."""
    user_crud = CRUDUser(db)
    user_by_email = await user_crud.get_by_email(email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует."
        )
    
    # Проверка на существующее имя пользователя (если оно передается и должно быть уникальным)
    # В вашей модели UserCreate есть username, и на него есть уникальный индекс в MongoDB
    # Мы можем добавить явную проверку или положиться на обработку DuplicateKeyError ниже.
    # Для чистоты, можно сначала проверить get_by_username, если такая функция есть в CRUDUser.
    # Если нет, то обработка DuplicateKeyError покроет этот случай.

    try:
        created_user = await user_crud.create(user_in=user_in)
    except DuplicateKeyError as e:
        # Проверяем, что ошибка связана с индексом username
        # Более точная проверка: if e.details and "keyPattern" in e.details and "username" in e.details["keyPattern"]:
        if hasattr(e, 'details') and isinstance(e.details, dict) and e.details.get("keyPattern", {}).get("username") == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем пользователя уже существует."
            )
        # Если ошибка дублирования не по username или детали не соответствуют ожидаемому формату
        # Можно логировать e для отладки, чтобы понять структуру ошибки от вашей версии MongoDB/Motor
        # logger.error(f"DuplicateKeyError during user registration: {e.details}") 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Ошибка данных клиента
            detail="Пользователь с таким email или именем пользователя уже существует."
        )

    # В реальном приложении здесь может быть отправка письма для подтверждения email
    # Сериализуем created_at в ISO формат перед возвратом
    created_user_dict = created_user.model_dump()
    created_user_dict['created_at'] = created_user_dict['created_at'].isoformat()
    return UserPublic(**created_user_dict)

@router.post("/token", response_model=TokenResponse, include_in_schema=True)
async def login_for_access_token_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    """Получение access и refresh токенов по логину и паролю (для OAuth2 password flow)."""
    # form_data.username здесь будет содержать email
    user = await _authenticate_user(email=form_data.username, password=form_data.password, db=db)
    return await _create_token_response(user=user, db=db)

@router.post("/login", response_model=TokenResponse)
async def login_for_access_tokens(
    login_data: UserLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    """Получение access и refresh токенов по логину и паролю (через JSON)."""
    user = await _authenticate_user(email=login_data.email, password=login_data.password, db=db)
    return await _create_token_response(user=user, db=db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    """Обновление access токена с использованием refresh токена."""
    # Ищем refresh токен в базе данных
    refresh_token = await db[REFRESH_TOKENS_COLLECTION].find_one({
        "refresh_token": token_data.refresh_token,
        "is_revoked": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}  # Токен не истек
    })
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя
    user_crud = CRUDUser(db)
    user = await user_crud.get_by_id(user_id=refresh_token["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, access_token_expires = _create_access_token_for_user(user)
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=token_data.refresh_token,
        expires_in=access_token_expires.total_seconds()
    ) 