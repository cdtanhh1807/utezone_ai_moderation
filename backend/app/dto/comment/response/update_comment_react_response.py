from pydantic import BaseModel
from typing import Optional
from models.post_model import CommentReact

class UpdateCommentReactResponse(BaseModel):
    message: str
    react: Optional[CommentReact] = None
