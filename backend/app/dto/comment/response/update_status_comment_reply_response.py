from models.commentreply_model import CommentReply
from pydantic import BaseModel


class UpdateStatusCommentReplyResponse(BaseModel):
    commentReply: CommentReply