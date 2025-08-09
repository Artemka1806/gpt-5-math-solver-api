import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..db import redis_client
from ..models.user import User

router = APIRouter(prefix="/user", tags=["user"])


class UpdateUserRequest(BaseModel):
    name: str | None = None
    avatar: str | None = None


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    cache_key = f"user:{user.id}"
    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    data = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar": user.avatar,
        "createdAt": user.created_at.isoformat(),
        "lastLogin": user.last_login.isoformat(),
        "role": user.role,
        "credits": user.credits,
        "subscriptionExpiresAt": user.subscription_expires.isoformat() if user.subscription_expires else None,
    }
    if redis_client:
        await redis_client.set(cache_key, json.dumps(data), ex=60)
    return data


@router.put("/me")
async def update_me(update: UpdateUserRequest, user: User = Depends(get_current_user)):
    for field, value in update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await user.save()
    if redis_client:
        await redis_client.delete(f"user:{user.id}")
    return await get_me(user)


@router.delete("/me")
async def delete_me(user: User = Depends(get_current_user)):
    await user.delete()
    if redis_client:
        await redis_client.delete(f"user:{user.id}")
    return {"message": "Account deleted"}
