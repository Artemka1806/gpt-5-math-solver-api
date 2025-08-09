from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Calculation(Document):
    user_id: str
    expression: str
    result_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "calculations"

