import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/user", tags=["user"])


class UpdateUserRequest(BaseModel):
    name: str | None = None
    avatar: str | None = None


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
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
    return data


@router.put("/me")
async def update_me(update: UpdateUserRequest, user: User = Depends(get_current_user)):
    for field, value in update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await user.save()
    return await get_me(user)


@router.delete("/me")
async def delete_me(user: User = Depends(get_current_user)):
    await user.delete()
    return {"message": "Account deleted"}
