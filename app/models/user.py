from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr


class User(Document):
    email: EmailStr
    name: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"
    credits: int = 1
    subscription_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
