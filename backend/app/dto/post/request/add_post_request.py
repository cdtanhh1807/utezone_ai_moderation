from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from models.post_model import PollData


class AddPostRequest(BaseModel):
    title: str
    content: str
    createdAt: datetime = datetime.now(timezone.utc)
    postType: str              # long | short
    visibility: str            # public | friends only | only me
    status: str
    createdBy: Optional[str] = None 
    category: Optional[List[str]] = None
    pollData: Optional[PollData] = None
    thumbnails: Optional[List[str]] = None

