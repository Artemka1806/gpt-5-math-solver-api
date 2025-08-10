from fastapi import APIRouter, Depends
from ..dependencies import require_admin
from ..models.user import User
from ..models.calculation import Calculation
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users")
async def list_users(page: int = 1, limit: int = 20):
    skip = (page - 1) * limit
    cursor = User.find().skip(skip).limit(limit)
    items = [
        {
            "id": str(u.id),
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "credits": u.credits,
            "subscriptionExpiresAt": u.subscription_expires.isoformat() if u.subscription_expires else None,
            "createdAt": u.created_at.isoformat(),
            "lastLogin": u.last_login.isoformat(),
        }
        async for u in cursor
    ]
    total = await User.count()
    return {"items": items, "page": page, "limit": limit, "total": total}


@router.patch("/users/{user_id}/role")
async def change_role(user_id: str, role: str):
    user = await User.get(user_id)
    if not user:
        return {"message": "User not found"}
    user.role = role
    await user.save()
    return {"id": user_id, "role": role}


class GrantRequest(BaseModel):
    credits: int | None = None
    subscription_days: int | None = None


@router.post("/users/{user_id}/grant")
async def grant(user_id: str, data: GrantRequest):
    user = await User.get(user_id)
    if not user:
        return {"message": "User not found"}
    if data.credits:
        user.credits = (user.credits or 0) + data.credits
    if data.subscription_days:
        base = (
            user.subscription_expires
            if user.subscription_expires and user.subscription_expires > datetime.utcnow()
            else datetime.utcnow()
        )
        user.subscription_expires = base + timedelta(days=data.subscription_days)
    await user.save()
    return {
        "id": user_id,
        "credits": user.credits,
        "subscriptionExpiresAt": user.subscription_expires.isoformat() if user.subscription_expires else None,
    }
