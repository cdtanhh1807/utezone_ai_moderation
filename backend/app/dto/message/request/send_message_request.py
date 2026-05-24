from typing import List, Optional

from pydantic import BaseModel

class SendMessageRequest(BaseModel):
    receiver_email: str
    content: Optional[str] = None
    file: Optional[List[str]] = None
    media: Optional[List[str]] = None
