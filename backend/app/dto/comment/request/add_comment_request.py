from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from models.post_model import CommentReact


class AddCommentRequest(BaseModel):
    postId: str
    content: str
    reacts: Optional[CommentReact] = None
    createdAt: datetime = datetime.now(timezone.utc)
    statusComment: str = "active"
    thumbnails: Optional[List[str]] = None
