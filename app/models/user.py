from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr


class User(Document):
    email: EmailStr
    name: Optional[str]
    avatar: Optional[str]
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
