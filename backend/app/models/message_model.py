from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel, EmailStr, Field
from models.base_model import PyObjectId
from bson import ObjectId


class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    sender_email: EmailStr
    receiver_email: EmailStr
    conversation_id: str          # "<min_email>_<max_email>"
    content: Optional[str] = None
    file: Optional[List[str]] = None
    file_id: Optional[List[str]] = None
    media: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"