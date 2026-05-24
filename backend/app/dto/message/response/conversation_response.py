from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class ConversationResponse(BaseModel):
    other_email: str
    full_name: str
    last_message: Optional[str] = Field(default=None)
    last_time: datetime
    has_new: bool