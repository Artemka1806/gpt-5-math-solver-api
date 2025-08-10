from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..models.user import User
from ..services.google_pay import verify_google_pay_token

router = APIRouter(prefix="/billing", tags=["billing"])


class GooglePayRequest(BaseModel):
    token: str
    credits: int | None = None
    subscription_days: int | None = None


@router.post("/google-pay")
async def google_pay_purchase(
    data: GooglePayRequest, user: User = Depends(get_current_user)
):
    valid = await verify_google_pay_token(data.token)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid payment token")
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
        "credits": user.credits,
        "subscriptionExpiresAt": user.subscription_expires.isoformat()
        if user.subscription_expires
        else None,
    }
