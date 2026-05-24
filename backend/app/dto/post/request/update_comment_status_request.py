from pydantic import BaseModel


class UpdateCommentStatusRequest(BaseModel):
    statusComment: str
    commentId: str
