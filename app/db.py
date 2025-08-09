import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from .core.config import settings
from .models.user import User
from .models.calculation import Calculation

mongo_client: AsyncIOMotorClient | None = None
redis_client: redis.Redis | None = None


async def init_db():
    global mongo_client, redis_client
    mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(database=mongo_client.get_default_database(), document_models=[User, Calculation])
    redis_client = redis.from_url(settings.redis_url)


async def close_db():
    if mongo_client:
        mongo_client.close()
    if redis_client:
        await redis_client.close()
