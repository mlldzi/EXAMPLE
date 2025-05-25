from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.user import UserCreate, UserPublic, UserUpdate, UserRole
from app.crud.user import CRUDUser
from app.api.v1.deps import get_db, get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserPublic:
    """Создать нового пользователя."""
    user_crud = CRUDUser(db)
    user = await user_crud.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует."
        )
    created_user = await user_crud.create(user_in=user_in)
    # Сериализуем created_at в ISO формат перед возвратом
    user_dict = created_user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    return UserPublic(**user_dict)

@router.get("/me", response_model=UserPublic)
async def read_current_user(
    current_user: UserPublic = Depends(get_current_user)
) -> UserPublic:
    """Получить информацию о текущем пользователе."""
    return current_user

@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserPublic:
    """Получить пользователя по ID."""
    user_crud = CRUDUser(db)
    user = await user_crud.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")
    
    # Сериализуем created_at в ISO формат перед возвратом
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    return UserPublic(**user_dict)

@router.get("/", response_model=List[UserPublic])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user)
) -> List[UserPublic]:
    """Получить список пользователей."""
    user_crud = CRUDUser(db)
    users = await user_crud.get_multiple(skip=skip, limit=limit)
    
    # Сериализуем created_at в ISO формат для каждого пользователя в списке
    users_list = []
    for user in users:
        user_dict = user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        users_list.append(UserPublic(**user_dict))
    
    return users_list

@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user)
) -> UserPublic:
    """Обновить данные пользователя."""
    if str(user_id) != str(current_user.id) and UserRole.ADMIN not in current_user.roles:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для выполнения операции")

    user_crud = CRUDUser(db)
    user = await user_crud.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

    updated_user = await user_crud.update(user_id=user_id, user_update=user_update)

    # Сериализуем created_at в ISO формат перед возвратом
    updated_user_dict = updated_user.model_dump()
    updated_user_dict['created_at'] = updated_user_dict['created_at'].isoformat()
    return UserPublic(**updated_user_dict)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user)
):
    """Удалить пользователя."""
    if str(user_id) != str(current_user.id) and UserRole.ADMIN not in current_user.roles:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для выполнения операции")

    user_crud = CRUDUser(db)
    deleted_successfully = await user_crud.delete(user_id=user_id)

    if not deleted_successfully:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден или уже был удален")
    
    # Если все прошло успешно, FastAPI автоматически вернет 200 OK
    # Можно вернуть кастомный ответ, если нужно
    return {"message": "Пользователь успешно удален"} # Пример ответа

# TODO: Добавить эндпоинт для получения списка пользователей, если необходимо. 
# TODO: Добавить эндпоинт для получения пользователя по email, если необходимо. 
# TODO: Добавить эндпоинт для получения пользователя по username, если необходимо. 
