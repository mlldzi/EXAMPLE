# Database session and connection logic
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_client = MongoDB() # Переименовал, чтобы не конфликтовать с возможным db из других контекстов

async def get_database() -> AsyncIOMotorDatabase:
    if db_client.db is None:
        raise Exception("Database not initialized. Call connect_to_mongo first.")
    return db_client.db

# Константы коллекций (будут добавлены позже по мере необходимости)
USERS_COLLECTION = "users"
PROFILES_COLLECTION = "profiles"
REFRESH_TOKENS_COLLECTION = "refresh_tokens"
TOKEN_BLACKLIST_COLLECTION = "token_blacklist"

async def connect_to_mongo():
    db_client.client = AsyncIOMotorClient(settings.MONGO_URI, uuidRepresentation='standard')
    db_client.db = db_client.client[settings.MONGO_DB_NAME]
    print(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")
    await create_indexes(db_client.db)

async def close_mongo_connection():
    if db_client.client:
        db_client.client.close()
        print("MongoDB connection closed")

async def create_indexes(db: AsyncIOMotorDatabase):
    # User collection indexes
    await db[USERS_COLLECTION].create_index("email", unique=True)
    await db[USERS_COLLECTION].create_index("username", unique=True, sparse=True) # Если username опционален
    await db[USERS_COLLECTION].create_index("id", unique=True)
    
    # Profile collection indexes (если будет)
    # await db[PROFILES_COLLECTION].create_index("user_id", unique=True)

    # Refresh token indexes
    await db[REFRESH_TOKENS_COLLECTION].create_index("refresh_token", unique=True)
    await db[REFRESH_TOKENS_COLLECTION].create_index("user_id")
    await db[REFRESH_TOKENS_COLLECTION].create_index("expires_at")
    
    # Token blacklist indexes
    await db[TOKEN_BLACKLIST_COLLECTION].create_index("token", unique=True)
    await db[TOKEN_BLACKLIST_COLLECTION].create_index("expires_at")
    
    print("Indexes created successfully for monolith app") 