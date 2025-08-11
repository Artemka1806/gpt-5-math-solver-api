from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, status, Form
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from fastapi.responses import RedirectResponse

from ..models.user import User
from ..core.security import create_token, verify_token
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    idToken: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: dict


class TestUserRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    avatar: str | None = None


@router.post("/test-user", response_model=TokenResponse)
async def create_test_user(data: TestUserRequest):
    user = await User.find_one(User.email == data.email)
    if not user:
        user = User(email=data.email, name=data.name, avatar=data.avatar, subscription_expires=None)
        await user.insert()
    if user.credits is None:
        user.credits = 1
        await user.save()
    access = create_token({"sub": str(user.id), "role": user.role})
    refresh = create_token(
        {"sub": str(user.id), "type": "refresh"},
        timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    return TokenResponse(
        accessToken=access,
        refreshToken=refresh,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar": user.avatar,
            "credits": user.credits,
            "subscriptionExpiresAt": user.subscription_expires.isoformat() if user.subscription_expires else None,
        },
    )


@router.post("/google-login")
async def google_login(
    request: Request,
    idToken: str | None = None,
    credential: str | None = Form(default=None),
):
    # Accept either JSON body with {"idToken"} or form with "credential" from Google Identity Services
    if not idToken and credential:
        idToken = credential
    if not idToken:
        # Try to parse JSON if sent as application/json
        try:
            body = await request.json()
            if isinstance(body, dict):
                idToken = body.get("idToken") or body.get("credential")
        except Exception:
            pass
    if not idToken:
        raise HTTPException(status_code=422, detail="Missing idToken/credential")

    audience = settings.google_client_id or None
    try:
        info = google_id_token.verify_oauth2_token(
            idToken, google_requests.Request(), audience
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID token") from e

    user = await User.find_one(User.email == info.get("email"))
    if not user:
        user = User(
            email=info.get("email"),
            name=info.get("name"),
            avatar=info.get("picture"),
            subscription_expires=None,
        )
        await user.insert()
    if user.credits is None:
        user.credits = 1
        await user.save()
    access = create_token({"sub": str(user.id), "role": user.role})
    refresh = create_token(
        {"sub": str(user.id), "type": "refresh"},
        timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    return RedirectResponse(url=f"{settings.redirect_url}?accessToken={access}&refreshToken={refresh}", status_code=status.HTTP_303_SEE_OTHE)


class RefreshRequest(BaseModel):
    refreshToken: str


@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    payload = verify_token(data.refreshToken)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access = create_token(
        {"sub": payload.get("sub"), "role": payload.get("role", "user")}
    )
    return {"accessToken": access}


class LogoutRequest(BaseModel):
    refreshToken: str | None = None


@router.post("/logout")
async def logout(_: LogoutRequest):
    return {"message": "Logged out successfully"}
