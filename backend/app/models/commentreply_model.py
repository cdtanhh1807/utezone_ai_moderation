from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

from models.post_model import CommentReact

# class React(BaseModel):
#     love: Optional[List[str]] = []
#     like: Optional[List[str]] = []
#     haha: Optional[List[str]] = []
#     wow: Optional[List[str]] = []
#     sad: Optional[List[str]] = []
#     angry: Optional[List[str]] = []

class CommentReply(BaseModel):  
    commentId: str
    commentBy: str
    postId: str
    path: str
    content: str
    createdAt: datetime
    status: str
    react: Optional[CommentReact] = Field(default_factory=CommentReact)
    thumbnails: Optional[List[str]] = Field(default_factory=list)
    thumbnails_url: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}