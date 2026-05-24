from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from models.post_model import PollData


class SharePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    createdAt: Optional[datetime] = datetime.now(timezone.utc)
    postType: Optional[str] = None              # long | short
    visibility: Optional[str] = None
    status: Optional[str] = None
    createdBy: Optional[str] = None 
    category: Optional[List[str]] = None
    pollData: Optional[PollData] = None
    thumbnails: Optional[List[str]] = None
    postId: Optional[str] = None

