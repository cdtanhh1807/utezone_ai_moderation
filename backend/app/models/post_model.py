from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

class React(BaseModel):
    love: Optional[List[str]] = []
    like: Optional[List[str]] = []
    haha: Optional[List[str]] = []
    wow: Optional[List[str]] = []
    sad: Optional[List[str]] = []
    angry: Optional[List[str]] = []

class PollData(BaseModel):
    questions: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    status: Optional[str] = "active"

class HistoryEdit(BaseModel):
    historyTitle: str
    historyContent: str
    historyCategory: str
    editedAt: datetime

class CommentReact(BaseModel):
    love: Optional[List[str]] = []
    like: Optional[List[str]] = []
    haha: Optional[List[str]] = []
    wow: Optional[List[str]] = []
    sad: Optional[List[str]] = []
    angry: Optional[List[str]] = []

class Comment(BaseModel):
    commentId: str
    commentBy: str
    content: str
    reacts: CommentReact
    createdAt: datetime
    statusComment: str
    thumbnails: Optional[List[str]] = Field(default_factory=list)
    thumbnails_url: Optional[List[str]] = Field(default_factory=list)

class Post(BaseModel):  
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    content: str
    createdAt: Optional[datetime] = Field(default_factory=datetime.now)
    postType: str              # long | short
    visibility: str            # public | friends only | only me
    status: str                # active | draft | deleted
    createdBy: str             # user id
    category: Optional[List[str]] = []
    thumbnails: Optional[List[str]] = []
    views: int = 0
    react: Optional[React] = None
    pollData: Optional[PollData] = None
    historyEdits: Optional[List[HistoryEdit]] = []
    comments: Optional[List[Comment]] = []
    lastEdited: Optional[datetime] = None
    postId: Optional[str] = None

    thumbnails: Optional[List[str]] = Field(default_factory=list)
    thumbnails_url: Optional[List[str]] = Field(default_factory=list)
    
    ai_summary: Optional[str] = None

    ai_moderation: Optional[Dict] = Field(
        default=None,
        description="Kết quả kiểm duyệt AI: {approved, scores, confidence, moderated_at, model}"
    )
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}