from pydantic import BaseModel
from typing import Optional
from models.post_model import CommentReact

class UpdateCommentReactRequest(BaseModel):
    id: str
    react: Optional[CommentReact] = None
