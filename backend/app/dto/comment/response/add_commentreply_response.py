from pydantic import BaseModel
from typing import Optional, Dict
from models.commentreply_model import CommentReply

class AddCommentReplyResponse(BaseModel):
    commentReply: CommentReply
