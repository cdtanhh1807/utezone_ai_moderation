from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from models.post_model import CommentReact


class AddCommentReplyRequest(BaseModel):
    postId: str
    parentId: Optional[str] = None
    path: Optional[str] = None
    content: str
    commentBy: Optional[str] = None
    thumbnails: Optional[List[str]] = None
