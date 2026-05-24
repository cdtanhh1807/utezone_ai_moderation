from pydantic import BaseModel


class UpdateStatusCommentReplyRequest(BaseModel):
    postId: str
    commentId: str
    path: str
    status: str
