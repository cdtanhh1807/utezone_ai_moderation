from pydantic import BaseModel
from typing import List, Optional, Dict
from models.commentreply_model import CommentReply

class GetCommentReplyResponse(BaseModel):
    commentReplys: List[CommentReply]
