from datetime import timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

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
        user = User(email=data.email, name=data.name, avatar=data.avatar)
        await user.insert()
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
        },
    )


@router.post("/google-login", response_model=TokenResponse)
async def google_login(data: GoogleLoginRequest):
    try:
        info = google_id_token.verify_oauth2_token(
            data.idToken, google_requests.Request(), None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID token") from e

    user = await User.find_one(User.email == info.get("email"))
    if not user:
        user = User(
            email=info.get("email"),
            name=info.get("name"),
            avatar=info.get("picture"),
        )
        await user.insert()
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
        },
    )


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
