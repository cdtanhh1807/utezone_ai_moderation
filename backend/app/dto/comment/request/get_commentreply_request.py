from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from models.post_model import CommentReact


class GetCommentReplyRequest(BaseModel):
    postId: str
    parentId: str
